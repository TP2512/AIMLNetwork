import logging
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
import pandas as pd

from InfrastructureSVG.Projects.General.MTBF.Diagram import Diagram
from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import print_before_logger, BuildLogger


@dataclass
class MTBFData:
    name: str
    start_time: datetime
    end_time: datetime
    crashes_datetime: list
    recoveries_datetime: list
    core_occurrences_count: int

    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.crashes_datetime, self.recoveries_datetime) == (other.crashes_datetime, other.recoveries_datetime)


class MTBFGenerator:
    def __init__(self, mtbf_data: MTBFData):
        self.logger = logging.getLogger('InfrastructureSVG.Logger_Infrastructure.Projects_Logger.' + self.__class__.__name__)

        self.mtbf_data = mtbf_data

        self.crashes_datetime = mtbf_data.crashes_datetime
        self.recoveries_datetime = mtbf_data.recoveries_datetime

        # self.num_crashes = len(self.crashes_datetime) + 1
        self.num_crashes = mtbf_data.core_occurrences_count

        self.visualization = Diagram()

    def mtbf_creator(self) -> float:

        if not self.crashes_datetime:
            # mtbf is system runtime
            mtbf = (self.mtbf_data.end_time - self.mtbf_data.start_time).seconds

        else:
            # calculated in seconds
            time_delta_in_sec = 0

            for inx, time in enumerate(self.crashes_datetime):
                if inx < len(self.recoveries_datetime):
                    time_delta = abs(time - self.recoveries_datetime[inx])
                    time_delta_in_sec += time_delta.total_seconds()
                    self.logger.debug(f'time delta in seconds - {time_delta_in_sec}')
            if self.num_crashes:
                mtbf = time_delta_in_sec / self.num_crashes
            else:
                mtbf = time_delta_in_sec
        self.logger.info(f'mtbf result in seconds - {mtbf}')
        mtbf = float('%.2f' % (mtbf / 60))
        self.logger.info(f'mtbf result in minutes - {mtbf}')

        return mtbf

    def create_log_runtime_seconds_range(self) -> list:
        # creating X axis to be equal to datetime range in seconds
        date_generated_seconds = [
            self.mtbf_data.start_time + timedelta(seconds=x)
            for x in range(
                (self.mtbf_data.end_time - self.mtbf_data.start_time).seconds
            )
        ]
        # self.logger.debug(f'sorted datetime in seconds list- {date_generated_seconds}')
        date_generated_seconds.append(self.mtbf_data.end_time)
        x = date_generated_seconds
        return x

    def create_crash_recovery_list(self, x: list) -> list:   # 0 indicates crash 1 indicates recovery
        crashes_time_range = []
        for inx, time in enumerate(self.crashes_datetime):
            crashes_time_range.extend(
                [
                    time + timedelta(seconds=x)
                    for x in range((self.recoveries_datetime[inx] - time).seconds)
                ]
            )

        y = []
        for time in x:
            if time in crashes_time_range:
                y.append(0)
            else:
                y.append(1)

        return y


def calc_system_mtbf_and_return_system_obj(dataframe: pd.DataFrame, y_label: str, x_label: str, menu: str, start_times: list, end_times: list, mtbf_data_list: list) -> MTBFData:
    logger_ = logging.getLogger('InfrastructureSVG.Logger_Infrastructure.Projects_Logger.' + "mtbf System data")
    logger_.debug('generate system mtbf data')
    start_times = sorted(start_times)
    end_times = sorted(end_times)

    x = dataframe.loc[dataframe[menu] == "System", x_label].tolist()
    y = dataframe.loc[dataframe[menu] == "System", y_label].tolist()
    system_crashes = []
    system_recoveries = []
    for inx, time in enumerate(x):
        if inx == 0:
            if y[inx] == 0:
                system_crashes.append(time)
        elif y[inx-1] != y[inx]:
            if y[inx] == 0:
                system_crashes.append(time)
            elif y[inx] == 1:
                system_recoveries.append(time)

    core_occurrences_count = sum(
        mtbf.core_occurrences_count for mtbf in mtbf_data_list
    )

    logger_.debug(f'System cores- {system_crashes}')
    logger_.debug(f'System recoveries- {system_recoveries}')

    return MTBFData(name='System', start_time=start_times[0], end_time=end_times[len(end_times) - 1],
                    crashes_datetime=system_crashes, recoveries_datetime=system_recoveries, core_occurrences_count=core_occurrences_count)


def create_overall_system_mtbf_data(df: pd.DataFrame, y_label: str, x_label: str, menu: str) -> pd.DataFrame:
    unique_df_time_list = df[x_label].unique()
    unique_df_time_list = sorted(unique_df_time_list)

    y = []
    for time in unique_df_time_list:
        up_down_array = (df.loc[df[x_label] == time, y_label]).to_numpy()

        if 0 in up_down_array:
            y.append(0)
        else:
            y.append(1)

    log_system_data = {x_label: unique_df_time_list, y_label: y, menu: ['System'] * len(y)}
    system_df = pd.DataFrame(log_system_data)

    return pd.concat([system_df, df])


def create_mtbf_and_visualization(diagram_path: str, execution_id: str, mtbf_data_list: list) -> tuple:
    logger_ = logging.getLogger('InfrastructureSVG.Logger_Infrastructure.Projects_Logger.' + "mtbf and visualization")
    logger_.debug('mtbf and visualization')

    y_label = 'Up/Down'
    x_label = 'Time'
    menu = 'name'
    title = 'Log Runtime'

    system_crashes = []
    system_recoveries = []
    start_times = []
    end_times = []

    df_list = []
    for mtbf in mtbf_data_list:
        system_crashes.extend(mtbf.crashes_datetime)
        system_recoveries.extend(mtbf.recoveries_datetime)
        start_times.append(mtbf.start_time)
        end_times.append(mtbf.end_time)

        mtbf_obj = MTBFGenerator(mtbf)
        mtbf_obj.mtbf_creator()

        x = mtbf_obj.create_log_runtime_seconds_range()
        x_only_time = [time.time() for time in x]
        y = mtbf_obj.create_crash_recovery_list(x)

        log_data = {x_label: x, y_label: y, menu: [mtbf.name] * len(x_only_time)}
        df = pd.DataFrame(log_data)
        df_list.append(df)

    dataframe = pd.concat(df_list)
    dataframe = create_overall_system_mtbf_data(df=dataframe, y_label=y_label, x_label=x_label, menu=menu)
    if 0 in dataframe[y_label].tolist():
        Diagram().create_line_diagram(data=dataframe, title=title, y_label=y_label, x_label=x_label, menu=menu, execution_id=execution_id, diagram_path=diagram_path)

    mtbf_data_system_obj = calc_system_mtbf_and_return_system_obj(dataframe=dataframe, y_label=y_label, x_label=x_label, menu=menu, start_times=start_times, end_times=end_times, mtbf_data_list=mtbf_data_list)
    mtbf_system_obj = MTBFGenerator(mtbf_data_system_obj)
    mtbf_system_value = mtbf_system_obj.mtbf_creator()

    logger_.info(f'mtbf value- {mtbf_system_value}')
    logger_.info(f'mtbf system data obj- {mtbf_data_system_obj}')
    return mtbf_system_value, mtbf_data_system_obj


def main():
    # create data object
    name = 'CU'
    start_time_ = datetime(2022, 3, 13, 12, 0, 0)
    end_time_ = datetime(2022, 3, 13, 17, 23, 13)
    # datetime(year, month, day, hour, minute, second, microsecond)
    crashes_datetime_ = [datetime(2022, 3, 13, 14, 6, 13), datetime(2022, 3, 13, 16, 7, 10), datetime(2022, 3, 13, 17, 11, 13)]
    recoveries_datetime_ = [datetime(2022, 3, 13, 15, 6, 50), datetime(2022, 3, 13, 17, 8, 3), datetime(2022, 3, 13, 17, 20, 13)]
    mtbf_data_cu_obj = MTBFData(name=name, start_time=start_time_, end_time=end_time_, crashes_datetime=crashes_datetime_, recoveries_datetime=recoveries_datetime_)

    # create data object
    name = 'DU'
    start_time_ = datetime(2022, 3, 13, 11, 0, 0)
    end_time_ = datetime(2022, 3, 13, 17, 2, 13)
    # datetime(year, month, day, hour, minute, second, microsecond)
    crashes_datetime_ = [datetime(2022, 3, 13, 11, 6, 10), datetime(2022, 3, 13, 13, 7, 10), datetime(2022, 3, 13, 15, 8, 13)]
    recoveries_datetime_ = [datetime(2022, 3, 13, 11, 15, 50), datetime(2022, 3, 13, 14, 8, 23), datetime(2022, 3, 13, 16, 20, 13)]
    mtbf_data_du_obj = MTBFData(name=name, start_time=start_time_, end_time=end_time_, crashes_datetime=crashes_datetime_, recoveries_datetime=recoveries_datetime_)

    execution_id = "1"
    diagram_path = "C:/Users/opeltzman/AirspanSprints/MTBF_sprint"
    create_mtbf_and_visualization(diagram_path=diagram_path, execution_id=execution_id, mtbf_data_list=[mtbf_data_cu_obj, mtbf_data_du_obj])


if __name__ == '__main__':
    # Create logger
    project_name = 'MTBF_Generator'
    site = 'IL SVG'
    print_before_logger(project_name=project_name, site=site)
    logger = BuildLogger(project_name=project_name, site=site).build_logger(debug=True)

    main()
