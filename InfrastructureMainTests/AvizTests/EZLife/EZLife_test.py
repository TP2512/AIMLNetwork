from InfrastructureSVG.EZLife.EZLifeMethods import EZLifeMethod
from InfrastructureMainTests.AvizTests.EZLife.GlobalParametersTest import GlobalParameters, GlobalClassAndFunctions


def main():
    global_parameters = GlobalParameters()

    ezlife_method = EZLifeMethod(global_parameters=global_parameters, global_class_and_functions=GlobalClassAndFunctions)

    status_code, ezlife_obj = ezlife_method.ezlife_get.get_by_url(url=f'{global_parameters.base_url}/GnodeBApp/1/')
    x = ezlife_obj[0]['cuup_gnodeb']
    print(x)
    print()


if __name__ == '__main__':
    from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import print_before_logger, BuildLogger

    project_name, site = 'Test', 'IL SVG'
    print_before_logger(project_name=project_name, site=site)
    logger = BuildLogger(project_name=project_name, site=site).build_logger(class_name=True, timestamp=True, debug=False)

    main()
