from datetime import datetime, timedelta
from dataclasses import dataclass
from InfrastructureSVG.Projects.General.MTBF.MTBF_Generator import MTBFData


@dataclass
class MTBGJiraData:
    MTBF_CORE_OCCURRENCE_COUNT: int
    CORE_OCCURRENCE_COUNT: int
    MIN_RUN_TIME: timedelta
    MAX_RUN_TIME: timedelta
    TIME_TO_FIRST_CRASH: timedelta
    SCENARIO_RUN_TIME: int
    CORE_SYSTEM_UPTIME: int


def min_and_max_run_time(start_time: datetime, end_time: datetime, crashes_datetime: list, recoveries_datetime: list) -> dict:
    up_list = [start_time] + recoveries_datetime
    down_list = crashes_datetime + [end_time]

    run_times = [
        down_list[inx] - up_list[inx]
        for inx in range(len(up_list))
    ]

    return {'max': max(run_times), 'min': min(run_times)}


def time_to_first_crash(start_time: datetime, crashes_datetime: list) -> timedelta:
    return crashes_datetime[0] - start_time if crashes_datetime else None


def mtbf_core_occurrences_count(crashes_datetime: list) -> int:
    return len(crashes_datetime)


def system_up_time(end_time: datetime, crashes_datetime: list, recoveries_datetime: list, scenario_run_time: int) -> int:
    down_list = crashes_datetime
    up_list = recoveries_datetime
    if len(down_list) > len(up_list):
        up_list.append(end_time)

    if not down_list:
        return scenario_run_time

    crashes_time = []
    length = len(down_list)
    inx = length - 1

    while inx >= 0:
        # print(up_list[inx] - down_list[inx])

        crashes_time.append(up_list[inx] - down_list[inx])
        inx -= 1

    total_system_crash_time = sum(crashes_time, timedelta())
    # convert timedelta to seconds
    # total_system_crash_time = (total_system_crash_time.seconds // 60) % 60
    total_system_crash_time = total_system_crash_time.seconds // 60
    # print(total_system_crash_time)
    # print(scenario_run_time - total_system_crash_time)

    return scenario_run_time - total_system_crash_time


def create_mtbf_jira_object(mtbf_data: MTBFData, mtbf_results) -> MTBGJiraData:
    # change the core count
    mtbf_core_occurrences_count_ = mtbf_data.core_occurrences_count
    # mtbf_core_occurrences_count_ = mtbf_core_occurrences_count(crashes_datetime=mtbf_data.crashes_datetime)
    core_occurrences_count_ = mtbf_core_occurrences_count_
    run_time_dict = min_and_max_run_time(start_time=mtbf_data.start_time, end_time=mtbf_data.end_time, crashes_datetime=mtbf_data.crashes_datetime,
                                         recoveries_datetime=mtbf_data.recoveries_datetime)
    min_run_time_ = run_time_dict['min']
    max_run_time_ = run_time_dict['max']
    time_to_first_crash_ = time_to_first_crash(start_time=mtbf_data.start_time, crashes_datetime=mtbf_data.crashes_datetime)
    core_system_up_time = system_up_time(end_time=mtbf_data.end_time, crashes_datetime=mtbf_data.crashes_datetime,
                                         recoveries_datetime=mtbf_data.recoveries_datetime, scenario_run_time=mtbf_results.SCENARIO_RUN_TIME)

    return MTBGJiraData(MTBF_CORE_OCCURRENCE_COUNT=mtbf_core_occurrences_count_, CORE_OCCURRENCE_COUNT=core_occurrences_count_,
                        MIN_RUN_TIME=min_run_time_, MAX_RUN_TIME=max_run_time_, TIME_TO_FIRST_CRASH=time_to_first_crash_, SCENARIO_RUN_TIME=mtbf_results.SCENARIO_RUN_TIME,
                        CORE_SYSTEM_UPTIME=core_system_up_time)


if __name__ == '__main__':
    name = 'CU'
    start_time_ = datetime(2022, 3, 13, 12, 0, 0)
    end_time_ = datetime(2022, 3, 13, 18, 20, 13)

    crashes_datetime_ = [datetime(2022, 3, 13, 14, 6, 13), datetime(2022, 3, 13, 16, 7, 10), datetime(2022, 3, 13, 17, 8, 33)]
    recoveries_datetime_ = [datetime(2022, 3, 13, 15, 6, 50), datetime(2022, 3, 13, 17, 8, 23), datetime(2022, 3, 13, 17, 20, 13)]

    mtbf_data_obj = MTBFData(name=name, start_time=start_time_, end_time=end_time_, crashes_datetime=crashes_datetime_, recoveries_datetime=recoveries_datetime_)
    create_mtbf_jira_object(mtbf_data_obj)
