def get_params(environment_objs):
    dut_dict = {
        '4g': {'dut': 'enb', 'acp': 'acp_name', 'type': 'enb'},
        '5g': {'dut': 'ru', 'acp': 'gnb_acp_name', 'type': 'gnb'},
    }
    protocol = environment_objs.jenkins_args["protocol"]
    dut = dut_dict[protocol]['dut']
    acp = dut_dict[protocol]['acp']
    dut_type = dut_dict[protocol]['type']
    return protocol, dut, acp, dut_type
