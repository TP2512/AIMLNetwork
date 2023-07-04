from InfrastructureSVG.Projects.General.TenableScanAndReport.TenableProcess import TenableProcess


def robot_process(node_name, ip_address, site, username, password, credential_type, folder_path='\\\\192.168.127.247\\TenableScans',
                  bs_hw_type='undefined', entity_version=None, entity_type=None, kernel_version=None, severity=None, scan_id=None):
    if site == 'IL SVG':
        tenable_scanner_name = 'asil-svg-nessus-scanner'  # IL
    elif site == 'IN SVG':
        tenable_scanner_name = 'ASIN-SVG-Nessus-Scanner'  # IND
    else:
        raise Exception('There is relevant site')

    node_name = f'SecurityScan: {node_name}'
    if bs_hw_type:
        node_name = f'{node_name}_{bs_hw_type}'
    if entity_version:
        node_name = f'{node_name}_{entity_version}'
    if kernel_version:
        node_name = f'{node_name}_{kernel_version}'
    print(f'The node_name is: {node_name}')

    defect_parameters_dict = {
        'entity_version': entity_version,
        'entity_type': entity_type,
        'bs_hw_type': bs_hw_type,
        'test_environments': ip_address,
    }

    tenable_process = TenableProcess()
    # defects_dict, download_to_path, download_to_path_csv, severity_details = tenable_process.tenable_process(
    defects_dict, download_to_path_pdf, download_to_path_csv, severity_details, plugin_id_to_defect = tenable_process.tenable_process(
        scan_id=scan_id,
        node_name=node_name,
        ip_address=ip_address,
        site=site,
        tenable_scanner_name=tenable_scanner_name,
        username=username,
        password=password,
        credential_type=credential_type,
        folder_path=folder_path,
        severity=severity,
        defect_parameters_dict=defect_parameters_dict
    )

    return defects_dict, download_to_path_pdf, severity_details


if __name__ == '__main__':
    node_name_ = 'AvizTest_22_9'
    ip_address_ = '1.1.1.1'
    site_ = 'IL SVG'

    username_ = 'root'
    password_ = 'airspan'
    credential_type_ = 'SSH'

    bs_hw_type_ = 'undefined'
    entity_version_ = 'entity_version_12345'
    entity_type_ = 'DU'
    kernel_version_ = 'kernel_version_12345'
    severity_ = ['Critical', 'High', 'Medium', 'Low']
    # severity_ = ['Critical']
    # severity_ = None

    defects_dict_, download_to_path_pdf_, severity_details_ = robot_process(
        # scan_id='1535',
        node_name=node_name_,
        ip_address=ip_address_,
        site=site_,
        username=username_,
        password=password_,
        credential_type=credential_type_,
        bs_hw_type=bs_hw_type_,
        entity_version=entity_version_,
        entity_type=entity_type_,
        kernel_version=kernel_version_,
        severity=severity_
    )
    print(f'defects_dict_ is: {defects_dict_}')
    print(f' download_to_path_ is: {download_to_path_pdf_}')
    print(f'severity_details_ is: {severity_details_}')

    print()
