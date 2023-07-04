*** Settings ***
Library  Collections
Library   RobotFrameworkSVGInfra.GraphCreator.Elasticsearch_visualisations.VegaVisualisationsRFI

Resource    ../../EZKeywords.robot


*** Keywords ***
Return Argument Example
    &{TestDic} =    Create Dictionary    test_key    test_val
    [Return]    ${TestDic}

