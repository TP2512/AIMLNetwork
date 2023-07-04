import arrow
import datetime
from datetime import datetime, timedelta
import logging
from dateutil import tz


class DateAndTimeManipulationsClass:
    def __init__(self):
        self.logger = logging.getLogger(f'InfrastructureSVG.Logger_Infrastructure.Projects_Logger.{self.__class__.__name__}')

    def remove_time_zone_from_date_and_time(self, time):
        """
           This function responsible for converting string TimeStamp to DateDndTime object
           and removing TimeZone value from it

           The function get 1 parameter:
               - "time" - parameter need to be a string

           The function return time object without TimeZone value
        """
        try:
            created = arrow.get(time)
            tmp_datetime_ = created.datetime
            return tmp_datetime_.replace(tzinfo=None)

        except Exception:
            self.logger.exception('')

    @staticmethod
    def convert_timestamp_to_local_time(time):
        import datetime
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz('Asia/Jerusalem')
        utc = datetime.datetime.strptime(time, '%Y/%m/%d %H:%M:%S')
        utc = utc.replace(tzinfo=from_zone)
        return utc.astimezone(to_zone).replace(tzinfo=None)

    def convert_time_to_seconds(self, time_):
        try:
            if len(time_) == 3:
                converted_time = time_
            else:
                time_to_convert = datetime.strptime(time_, '%H:%M:%S').time()
                # time_to_convert = time.strptime(time, '%H:%M:%S')

                converted_time = str(timedelta(hours=time_to_convert.hour, minutes=time_to_convert.minute,
                                               seconds=time_to_convert.second).total_seconds()).split('.')
                converted_time = converted_time[0]

            return converted_time

        except Exception:
            self.logger.exception('')

    @staticmethod
    def convert_minutes_to_days_and_time(minutes, time_to_crash=False):
        if not minutes or minutes == 0.0 or minutes == 0:
            return ('N/A', ['N/A']) if time_to_crash else 'N/A'
        minutes = max(minutes, 1)
        seconds = minutes * 60
        seconds_in_day = 60 * 60 * 24
        seconds_in_hour = 60 * 60
        seconds_in_minute = 60

        days = seconds // seconds_in_day
        if days == 0.0:
            days = 0
        hours = (seconds - (days * seconds_in_day)) // seconds_in_hour
        if hours == 0.0:
            hours = 0
        minutes = (seconds - (days * seconds_in_day) - (hours * seconds_in_hour)) // seconds_in_minute
        if minutes == 0.0:
            minutes = 0
        if days == 0 and minutes == 0:
            return ('N/A', ['N/A']) if time_to_crash else 'N/A'
        return (f'{int(days)}d:{int(hours)}h:{int(minutes)}m', [days, hours]) if time_to_crash else f'{int(days)}d:{int(hours)}h:{int(minutes)}m'

    @staticmethod
    def convert_str_time_to_sec(time_str: str):
        seconds = 0
        for part in time_str.split(':'):
            seconds = seconds * 60 + int(part, 10)
        return seconds

    @staticmethod
    def convert_str_time_to_sec2(time_str: str):
        time_str = time_str.split(':')
        hours = int(time_str[0]) * 3600
        minutes = int(time_str[1]) * 60
        seconds = int(time_str[2])

        return hours + minutes + seconds

    def convert_time_to_format(self, time_str):
        time_ = self.convert_str_time_to_sec(time_str)
        day = time_ // (24 * 3600)
        time_ = time_ % (24 * 3600)
        hour = time_ // 3600
        time_ %= 3600
        minutes = time_ // 60
        time_ %= 60
        seconds = time_
        print(f"d:h:m:s-> {day}:{hour}:{minutes}:{seconds}")

        return f'{day}:{hour}:{minutes}:{seconds}'
