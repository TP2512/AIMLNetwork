import json
import socket
from typing import Optional, Union

from InfrastructureMainTests.AvizTests.ACP.ACPInfra import ACPInfra
from InfrastructureSVG.EZLife.EZLifeMethods import EZLifeMethod

from InfrastructureMainTests.AvizTests.EZLife.GlobalParametersTest import GlobalParameters, GlobalClassAndFunctions


def main(
        hostname, ip_address, owner: str, acp_name: str, gnb_acp_names, vlan_number: str, k_master,
        acp_username: str = 'admin', acp_password: str = 'password', description: str = '', server_username: str = 'root',
        server_password: str = 'password'
):  # sourcery no-metrics
    acp_client = ACPInfra(
        acp_name=acp_name,
        username=acp_username,
        password=acp_password,
    )

    if not hostname:
        hostname = socket.gethostname()

    global_parameters = GlobalParameters()

    ezlife_method = EZLifeMethod(global_parameters=global_parameters, global_class_and_functions=GlobalClassAndFunctions)

    # Get Setup from EZLife
    status_code, setup_obj = ezlife_method.ezlife_get.get_setup_by_name(hostname)

    if not (setup_obj and len(setup_obj) > 0):
        # Build Setup on EZLife
        setup_data = {
            'en_dis': True,
            'owner': owner,
            'name': hostname,
            'site': 1,
            'acp': 25,
            'description': description,
            'domain_setup_name': hostname,
            'ip_address': ip_address,
            'vlan_number': vlan_number,
            'customer_name': 1,
        }
        status_code, setup_obj = ezlife_method.ezlife_post.create_setup(setup_data)
        if status_code not in [200, 201]:
            if setup_obj.text:
                logger.error(setup_obj.text)
            raise Exception('Setup object was not created')

    for gnb_acp_name in gnb_acp_names:
        # Get gNB Data from ACP
        entities_data_obj = acp_client.get_gnb_details(gnb_name=gnb_acp_name)
        logger.debug(json.dumps(entities_data_obj, sort_keys=True, indent=4, separators=(',', ': ')))
        if not entities_data_obj:
            raise Exception('There is no data from the ACP')

        # Build gNB on EZLife
        gnb_data = {
            'en_dis': True,
            'name': f'{gnb_acp_name}_[{hostname}]',
            'acp_name': f'{gnb_acp_name}_[{hostname}]',
            'description': description,
            'setup': setup_obj.json()['id'] if type(setup_obj) is not list else setup_obj[0]['id'],
        }
        status_code, gnb_obj = ezlife_method.ezlife_post.create_gnb(gnb_data)
        if status_code not in [200, 201]:
            if gnb_obj.text:
                logger.error(gnb_obj.text)
            raise Exception('gNB object was not created')

        # Build entities (CP, UP, DU and RU) on EZLife
        entity_obj = None
        for k, v in entities_data_obj.items():
            if k in ['gnb_name', 'gnbXpu']:
                continue

            entity_data = {
                'en_dis': True,
                'name': f'{v["managedElementId"]}_[{hostname}]',
                'acp_name': acp_name,
                'description': description,
                'ssh_ip_address': v['ip_address'],
                'server_username': server_username,
                'server_password': server_password,
                'k_master': k_master,
                'gnodeb': gnb_obj.json()['id'],
                'ssh_port': '22'
            }
            if k == 'gnbCuCp':
                cucp_data = {'hardware_type': 1} | entity_data

                status_code, entity_obj = ezlife_method.ezlife_post.create_cucp(cucp_data)

            elif k == 'gnbCuUp':
                cuup_data = {'hardware_type': 2} | entity_data

                status_code, entity_obj = ezlife_method.ezlife_post.create_cuup(cuup_data)

            elif k == 'gnbDu':
                du_data = {'hardware_type': 3} | entity_data

                status_code, entity_obj = ezlife_method.ezlife_post.create_du(du_data)

            elif k == 'gnbRu':
                ru_data = {'hardware_type': 4} | entity_data

                status_code, entity_obj = ezlife_method.ezlife_post.create_ru(ru_data)

            if status_code not in [200, 201]:
                if entity_obj.text:
                    logger.error(entity_obj.text)
                raise Exception(f'{k} object was not created')
        print()
    print()


def read_list(question: str) -> Union[str, None]:
    value: Optional[list] = None
    while value is None:
        _ = input(f"{question} ")
        try:
            value = _.split(',')
        except ValueError:
            logger.exception("Invalid input.")
    return value


def read_str(question: str) -> Union[str, None]:
    value: Optional[str] = None
    while value is None:
        _ = input(f"{question} ")
        try:
            value = str(_)
        except ValueError:
            logger.exception("Invalid input.")
    return value


def read_int(question: str, min_value: int = 0):
    value: Optional[int] = None
    while value is None or value < min_value:
        _ = input(f"{question} ")
        try:
            value = int(_)
        except ValueError:
            logger.exception("Invalid input. Please enter a number.")
    return value


if __name__ == '__main__':
    from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import print_before_logger, BuildLogger

    PROJECT_NAME = 'Build EZLife Full Setup by ACP'
    SITE = 'IL SVG'
    print_before_logger(project_name=PROJECT_NAME, site=SITE)
    logger = BuildLogger(project_name=PROJECT_NAME, site=SITE).build_logger(class_name=True, timestamp=True, debug=True)

    try:
        # main(
        #     hostname=read_str(question='Enter your hostname: '),
        #     ip_address=read_str(question='Enter your IP address: '),
        #     owner=read_str(question='Enter your domain username: '),
        #     acp_name=read_str(question='Enter your ACP name: '),
        #     vlan_number=read_str(question='Enter your setup vlan number: '),
        #     gnb_acp_names=[read_str(question='Enter your gNBs ACP name (Please separate the names using a comma ","): ')],
        #     k_master=read_str(question='Enter your k8S name from choices: '),
        # )

        main(
            hostname='ASIL-BMW1',
            ip_address='192.168.125.13',
            owner='spuser',
            acp_name='172.20.63.215',
            vlan_number='1040',
            gnb_acp_names=['ED085B0164A8'],
            k_master=47,
        )
    except Exception:
        logger.exception('')
    _ = read_str(question='Press Enter to exit.')
    print()
