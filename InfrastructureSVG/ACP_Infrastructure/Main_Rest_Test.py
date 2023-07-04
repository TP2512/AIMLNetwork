from InfrastructureSVG.ACP_Infrastructure.General_Actions import GeneralRESTACPActions
from InfrastructureSVG.ACP_Infrastructure.NBI_REST_API import ACPRestApi
from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import ProjectsLogging
# import urllib3
#
# urllib3.disable_warnings()

if __name__ == "__main__":
    # General Configuration:
    logger = ProjectsLogging('TP_Calculator_Infrastructure').project_logging()

    body_body_put_request_patch_request = {
        "name": "56789",
        "statsGranularityPeriod": 5,
        "hardwareCategory": "Aircard"
    }

    acp_name = 'asil-svg-acp5'
    # acp_name = '10.23.105.12'
    username = 'admin'
    password = 'password'
    node_name = 'xxxxx'

    # url = 'https://10.23.105.12/api/18.5'  # Manoj's ACP

    logger.info('Start')

    obj = ACPRestApi(acp_name=acp_name, username=username, password=password)
    response = obj.acp_get("nmsInfo")
    if response[0].status_code == 200:
        print(response[1]['NMSSoftwareVersion'])

    """User Parameters"""
    # user_parameters = {'acp_element_name': 'AircardProfile', 'element_profile_name': 'post_755'}
    # user_parameters = {'acp_element_name': 'DiscoveryTask', 'element_profile_name': ''}
    # user_parameters = {'acp_element_name': 'GnbDiscoveryTask', 'element_profile_name': ''}
    # user_parameters = {'acp_element_name': 'Gnb', 'element_profile_name': 'post_gnb_REST'}
    # user_parameters = {'acp_element_name': 'GnbRu', 'element_profile_name': 'post_gnb_REST'}
    # user_parameters = {'acp_element_name': 'GnbDiscoveredNetworkFunction',
    # 'gnbDiscoveredNetworkFunction': 'post_gnb_REST'}
    # user_parameters = {'acp_element_name': 'gnbDiscoveryTask', 'Name': 'post_discovery_REST'}
    # user_parameters = {'acp_element_name': 'discoveryTask', 'Name': 'post_discovery_REST'}
    # user_parameters = {'acp_element_name': 'gNb', 'gnbDiscoveryTask': 'test1111'}
    user_parameters = {'acp_element_name': 'gnbCucp', 'gnbDiscoveryTask': 'test1111'}
    # user_parameters = {'acp_element_name': 'alarm', 'AlarmType': 'SAS Server Disconnected'}

    """User POST Create action"""
    # body_post_request_aircard = {
    #     "name": user_parameters.get('element_profile_name'),
    #     "statsGranularityPeriod": 5,
    #     "hardwareCategory": "Aircard"
    # }
    # body_post_request_discovery_task = \
    #     {
    #         "name": "post_discovery_REST15",
    #         "snmpVersion": "Version2C",
    #         "enabled": True,
    #         "writeCommunity": "private",
    #         "readCommunity": "public",
    #         "ipAddressList": [
    #             {
    #                 "ipAddressFrom": "2.2.2.2",
    #                 "ipAddressTo": "2.2.2.2"
    #             }
    #         ],
    #         "portList": [
    #             "161"
    #         ]
    #     }
    #
    # post_rest_method_response, post_json_object_response = \
    #     obj.acp_post_create(acp_element_name=user_parameters.get('acp_element_name'),
    #                         body_request=body_post_request_discovery_task)
    # print()
    # """User PATCH action"""
    # body_patch_request = {
    #     "name": user_parameters.get('element_profile_name'),
    #     "statsGranularityPeriod": 30,
    #     "hardwareCategory": "Aircard"
    # }
    # patch_rest_method_response, patch_json_object_response = \
    #     obj.acp_patch(acp_shema_name=user_parameters.get('acp_shema_name'),
    #                   url_search=user_parameters.get('element_profile_name'),
    #                   body_request=body_patch_request)
    # logger.info(f"PATCH response:\n {patch_json_object_response}\n")
    #
    # """User DELETE action"""
    # element_profile_name = user_parameters.get('element_profile_name')
    # delete_rest_method_response, delete_json_object_response = \
    #     obj.acp_delete(acp_shema_name=user_parameters.get('acp_shema_name'),
    #                    url_search=element_profile_name)

    """User GET action"""
    get_rest_method_response, get_json_object_response = \
        obj.acp_get(acp_element_name=user_parameters.get('acp_element_name'), url_search=user_parameters.get(
            'element_profile_name'))
    print()
    # if type(get_json_object_response[0]["Id"]) is float:
    #     id_ = int(get_json_object_response[0]["Id"])
    # else:
    #     pass
    print()
    # patch - according to some

    # get
