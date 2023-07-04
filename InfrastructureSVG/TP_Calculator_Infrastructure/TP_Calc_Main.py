from InfrastructureSVG.Logger_Infrastructure.Projects_Logger import ProjectsLogging
from InfrastructureSVG.TP_Calculator_Infrastructure.TP_Calc_Methods import TPCalculatorPerDirection

if __name__ == '__main__':
    logger = ProjectsLogging('TP_Calculator_Infrastructure').project_logging()
    logger.info('Script Started!')

    jira_fields = {
        'max_throughput': True,
        # 'max_throughput': False,
        'frequency_band': 'n78',  # fdd
        # 'frequency_band': 'n38',  #tdd
        'dl_layers': 2,
        # 'dl_layers': 'xxx',
        'ul_layers': 1,
        'dl_max_modulation': 64,
        # 'dl_max_modulation': 256,
        'ul_max_modulation': 64,
        # 'ul_max_modulation': 256,
        'scs_value': 15,
        # 'scs_value': '',
        'bw_value': 10,
        # 'bw_value': 50,
        'mcs': 25,
        'dl_ca': 1,
        'ul_ca': 1,
        'bler': 0,
        'format': 2,
        # 'format': '',
        'dl_split': 70,
        # 'dl_split': '',
        'ul_split': 20,
        # 'ul_split': '',
        'ssf_split': 10,
        # 'ssf_split': '',
        # 'direction': 'ul ',
        # 'direction': 'Dl',
        'direction': 'biDi',
    }

    throughput = TPCalculatorPerDirection(**jira_fields)
    throughput.run_tp_calculator_per_direction()

    if not throughput.invalid_parameters_dict and hasattr(throughput, 'Throughput'):
        logger.info(throughput.Throughput)
    else:
        logger.info(throughput.invalid_parameters_dict)
        logger.info(throughput.err_message)

    print()
