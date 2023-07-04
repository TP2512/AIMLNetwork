import re


def remove_control_characters(file_path, new_file_path):
    with open(new_file_path, 'w') as output_file:
        with open(file_path, 'r') as input_file:
            file_content = input_file.read()
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            new_file_content = ansi_escape.sub('', file_content)
            output_file.write(new_file_content)


file_path = r"C:\Users\rblumberg\PycharmProjects\InfrastructureSVG\InfrastructureSVG\Files_Infrastructure\Log_Analyzer\data\test_logs\initial\CUCP_2021-08-19 11_21_44.log"
new_file_path = r"C:\Users\rblumberg\PycharmProjects\InfrastructureSVG\InfrastructureSVG\Files_Infrastructure\Log_Analyzer\data\test_logs\initial\CUCP_2021-08-19 11_21_44_output.log"
remove_control_characters(file_path, new_file_path)
