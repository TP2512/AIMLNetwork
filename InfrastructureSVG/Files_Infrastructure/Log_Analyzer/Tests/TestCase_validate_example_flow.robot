*** Settings ***
Documentation     This is a Log Analyzer
...
...               The Analyzer accepts a YAML file similar to Log_Analyzer\data\flows\example_flow_1.yml
...               and a log file.
...               It than parse them and validate if the log file follows the sequence flow defined in the YAML file
Library           ../LogAnalyzer.py

*** Variables ***
    ${validation_result} = False
*** Test Cases ***
Validate Example_flow
    [Arguments]    ${YAML_file}    ${log_file}
    Given The input validation has passed
    And Given The YAML file has been succesfully parsed
    Then the validation result is valid

*** Keywords ***
The input validation has passed
    [Arguments]    ${YAML_file}    ${log_file}
    LogAnalyzer.validate input    ${YAML_file}    ${log_file}


The YAML file has been succesfully parsed
the validation result is valid

