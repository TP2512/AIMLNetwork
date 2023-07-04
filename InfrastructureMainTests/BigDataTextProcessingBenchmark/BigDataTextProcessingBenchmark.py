import os
import re

from flashtext import KeywordProcessor
import logging
import json
import datetime
import subprocess
from io import StringIO

class BigDataTextProcessingBenchmark:

    def __init__(self):
        now_datetime = datetime.datetime.now(tz=datetime.timezone.utc)
        now_str = now_datetime.strftime('%Y%m%d-%H%M%S')
        self.logger = logging.getLogger('InfrastructureSVG.Logger_Infrastructure.Projects_Logger.' + self.__class__.__name__)
        self.debug_flag = False
        if self.debug_flag:
            self.input_file_path = os.path.join(os.path.dirname(__file__), 'data', 'text_files', 'debug_test_lines.log')
        else:
            self.input_file_path = os.path.join(os.path.dirname(__file__), 'data', 'text_files', 'inflated_text_file_2021_07_28-16_41_11.log')
        self.debug_test_lines_file_path = os.path.join(os.path.dirname(__file__), 'data', 'text_files', 'debug_test_lines.log')
        self.inflated_output_file_path = os.path.join(os.path.dirname(__file__), 'data', 'text_files', 'inflated_text_file_' + now_str + '.log')
        self.output_json_file_path = os.path.join(os.path.dirname(__file__), 'output', 'parsed_log_files', 'json_output_' + now_str + '.log')
        self.log_pattern = re.compile(r"\[(\d*)\] (\d\d)\/(\d\d)\/(\d\d\d\d) (\d\d):(\d\d):(\d\d):(\d\d\d)( <(.*?)> )? (.*)")
        self.KB_to_MB = 1 / 1024 / 1024
        self.sep_executable_path = r'C:\Program Files (x86)\GnuWin32\bin\sed.exe'
        self.perl_executable_path = r'C:\Strawberry\perl\bin\perl.exe'

    def run_benchmark(self):
        expression = 'PHY is RUNNING'
        is_inflate = False
        if is_inflate:
            inflate_up_to_size = 1000000000
            self.inflate_text_file_up_to_size(inflate_up_to_size, self.input_file_path, self.inflated_output_file_path)
        self.big_data_regex_test_perl(self.input_file_path, self.output_json_file_path, expression)

    @staticmethod
    def big_data_regex_test_python(input_file_path, expression):
        start_datetime = datetime.datetime.now(tz=datetime.timezone.utc)
        regex_match_found = True
        match_lines_numbers = []
        with open(input_file_path, 'r') as input_file:
            regexp = re.compile(expression)
            file = input_file.read()
            for line_index, line in enumerate(file.split('\n\n'), 1):
                if regexp.search(line):
                    match_lines_numbers.append(line_index)
        end_datetime = datetime.datetime.now(tz=datetime.timezone.utc)
        test_time = end_datetime - start_datetime
        return regex_match_found, test_time

    def big_data_regex_test_flashtext(self, input_file_path, output_json_file_path, keyword):
        start_datetime = datetime.datetime.now(tz=datetime.timezone.utc)
        self.logger.info(f"Flashtext test started at {start_datetime.strftime('%Y%m%d-%H%M%S')}")
        keyword_processor = KeywordProcessor()
        keyword_processor.add_keyword(keyword)
        input_file_size = os.stat(input_file_path).st_size * self.KB_to_MB
        with open(input_file_path, 'r') as input_file:
            input_file_lines = input_file.readlines()
            num_of_lines = len(input_file_lines)
            input_file.seek(0)
            input_file_str = input_file.read()
            print(datetime.datetime.now(datetime.timezone.utc))
            extracted_keywords = keyword_processor.extract_keywords(input_file_str, span_info=True)
            print(datetime.datetime.now(datetime.timezone.utc))
            self.logger.info(f'The extracted keywords are: {extracted_keywords}')
            extracted_keywords_line_numbers = []
            start_get_line_numbers_datetime = datetime.datetime.now(datetime.timezone.utc)
            extracted_keywords_with_line_numbers = self.get_line_numbers_of_extracted_keywords(extracted_keywords, input_file_str)
            end_get_line_numbers_datetime = datetime.datetime.now(datetime.timezone.utc)
            get_line_numbers_time = end_get_line_numbers_datetime - start_get_line_numbers_datetime
            self.logger.info(f"get line numbers time: {get_line_numbers_time}")
            json_dict_list = []
            test_lines_list = []
            for extracted_keyword_with_line_numbers in extracted_keywords_with_line_numbers:
                json_dict, line = self.get_line_as_json_dict(extracted_keyword_with_line_numbers['keyword_line_num'], input_file_lines)
                json_dict_list.append(json_dict)
                test_lines_list.append(line)
            self.write_test_lines(test_lines_list)
            self.write_test_json(json_dict_list)
        end_datetime = datetime.datetime.now(datetime.timezone.utc)
        test_time = end_datetime - start_datetime
        stats_str = self.output_stats(input_file_path, output_json_file_path, num_of_lines, input_file_size, test_time)
        self.logger.info(stats_str)
        self.logger.info(f"Flashtext test ended, the keyword: {keyword}, has been found in the following lines: {extracted_keywords_line_numbers}")
        self.logger.info(f"here is the created json: {json.dumps(json_dict_list, indent=4, sort_keys=True)}")
        self.logger.info(f"test took: {test_time}")
        self.logger.info(f"Flashtext test ended at {end_datetime.strftime('%Y%m%d-%H%M%S')}")

    def big_data_regex_test_sed(self, input_file_path, output_json_file_path, keyword):
        start_datetime = datetime.datetime.now(datetime.timezone.utc)
        self.logger.info(f"Sep test started at {start_datetime.strftime('%Y%m%d-%H%M%S')}")
        input_file_size = os.stat(input_file_path).st_size * self.KB_to_MB
        result = subprocess.run([self.sep_executable_path, '-n', "s/PHY is RUNNING/&/p", self.input_file_path], stdout=subprocess.PIPE)
        result_lines = StringIO(result.stdout.decode("utf-8"))
        json_dict_list = []
        test_lines_list = []
        num_of_lines = 0
        for line in result_lines:
            line = line.rstrip()
            json_dict = self.parse_line_to_json(line)
            json_dict_list.append(json_dict)
            test_lines_list.append(line)
            num_of_lines += 1
        # self.write_test_lines(test_lines_list)
        # self.write_test_json(json_dict_list)
        print(datetime.datetime.now(datetime.timezone.utc))
        end_datetime = datetime.datetime.now(datetime.timezone.utc)
        test_time = end_datetime - start_datetime
        stats_str = self.output_stats(input_file_path, output_json_file_path, num_of_lines, input_file_size, test_time)
        self.logger.info(stats_str)
        self.logger.info(f"Sep test ended")
        self.logger.info(f"here is the created json: {json.dumps(json_dict_list, indent=4, sort_keys=True)}")
        self.logger.info(f"test took: {test_time}")
        self.logger.info(f"Flashtext test ended at {end_datetime.strftime('%Y%m%d-%H%M%S')}")

    def big_data_regex_test_perl(self, input_file_path, output_json_file_path, keyword):
        start_datetime = datetime.datetime.now(datetime.timezone.utc)
        self.logger.info(f"Sep test started at {start_datetime.strftime('%Y%m%d-%H%M%S')}")
        input_file_size = os.stat(input_file_path).st_size * self.KB_to_MB
        result = subprocess.run([self.perl_executable_path, '-pi', '-e', "s/PHY is RUNNING/&/p", self.input_file_path], stdout=subprocess.PIPE)
        result_lines = StringIO(result.stdout.decode("utf-8"))
        json_dict_list = []
        test_lines_list = []
        num_of_lines = 0
        for line in result_lines:
            line = line.rstrip()
            json_dict = self.parse_line_to_json(line)
            json_dict_list.append(json_dict)
            test_lines_list.append(line)
            num_of_lines += 1
        # self.write_test_lines(test_lines_list)
        # self.write_test_json(json_dict_list)
        print(datetime.datetime.now(datetime.timezone.utc))
        end_datetime = datetime.datetime.now(datetime.timezone.utc)
        test_time = end_datetime - start_datetime
        stats_str = self.output_stats(input_file_path, output_json_file_path, num_of_lines, input_file_size, test_time)
        self.logger.info(stats_str)
        self.logger.info(f"Sed test ended")
        self.logger.info(f"here is the created json: {json.dumps(json_dict_list, indent=4, sort_keys=True)}")
        self.logger.info(f"test took: {test_time}")
        self.logger.info(f"Flashtext test ended at {end_datetime.strftime('%Y%m%d-%H%M%S')}")

    @staticmethod
    def get_line_numbers_of_extracted_keywords(extracted_keywords, input_file_str):
        extracted_keywords_dict_list = []
        for extracted_keyword in extracted_keywords:
            extracted_keywords_dict = {'keyword': extracted_keyword[0],
                                       'keyword_char_position': extracted_keyword[1],
                                       'keyword_line_num': len([c for c in input_file_str[:extracted_keyword[1]] if c == '\n']),
                                       }
            extracted_keywords_dict_list.append(extracted_keywords_dict)
        return extracted_keywords_dict_list

    def get_line_as_json_dict(self, line_num, input_file_lines):
        line = input_file_lines[line_num]
        json_dict = self.parse_line_to_json(line, line_num)
        return json_dict, line

    def parse_line_to_json(self, line):
        match = self.log_pattern.match(line)
        if not match:
            self.logger.error("The regex pattern matcher has failed")
        else:
            match_groups = match.groups()
            print("Log line:")
            line_datetime = self.parse_date_time_str(list(match_groups)[1:7])
            json_dict = {'id': match_groups[0], 'datetime': line_datetime, 'type': match_groups[9], 'text': match_groups[10]}
            return json_dict

    @staticmethod
    def parse_date_time_str(date_time_list):
        line_datetime = datetime.datetime(int(date_time_list[2]), int(date_time_list[1]), int(date_time_list[0]), int(date_time_list[3]),
                                          int(date_time_list[4]), int(date_time_list[5]))
        line_datetime_str = line_datetime.strftime('%Y%m%d-%H%M%S')
        return line_datetime_str

    def write_test_lines(self, lines_list):
        with open(self.debug_test_lines_file_path, 'w') as debug_test_lines_file:
            for line in lines_list:
                debug_test_lines_file.write("%s\n" % line)

    def write_test_json(self, json_dict_list):
        with open(self.output_json_file_path, 'w') as output_json_file:
            output_json_file.write(json.dumps(json_dict_list, indent=4, sort_keys=True))

    @staticmethod
    def inflate_text_file_up_to_size(inflate_up_to_size, input_file_path, inflated_output_file_path):
        file_size = os.stat(input_file_path).st_size
        num_of_iteration = inflate_up_to_size//file_size + 1
        new_file_text = ""
        with open(input_file_path, 'r') as input_file:
            file_text = input_file.read()
            for iteration_index in range(num_of_iteration):
                new_file_text += file_text
        with open(inflated_output_file_path, 'w') as output_file:
            output_file.write(new_file_text)

    @staticmethod
    def output_stats(input_file_path, output_json_file_path, num_of_lines, input_file_size, test_time):
        stats_str = ""
        stats_str += f"input_file_path: {input_file_path}\n"
        stats_str += f"output_json_file_path: {output_json_file_path}\n"
        stats_str += f"num_of_lines: {num_of_lines}\n"
        stats_str += f"input_file_size: {input_file_size}\n"
        stats_str += f"test_time: {test_time}\n"
        num_of_lines_metrics = 10000
        sec_per_metrics_lines = (num_of_lines/num_of_lines_metrics) / test_time.total_seconds()
        stats_str += f"sec_per_metrics_lines ({num_of_lines_metrics} lines): {sec_per_metrics_lines}\n"
        storage_size_metrics = 1
        sec_per_metrics_size = (input_file_size / storage_size_metrics) / test_time.total_seconds()
        stats_str += f"sec_per_metrics_size ({storage_size_metrics} MB): {sec_per_metrics_size}\n"
        return stats_str
