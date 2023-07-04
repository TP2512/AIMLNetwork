import re

from InfrastructureSVG.Network_Infrastructure.SSH_Infrastructure import SSHConnection


def get_demangle(ssh, bt_mangle):
    commands = [
        "d = cxxfilt.Demangler(find_library('c'), find_library('stdc++'))",
        f"demangle_output = d.demangle('{bt_mangle}')",
        "print(f'demangle is: {demangle_output}')",

    ]

    ssh.full_output = ''
    ssh.ssh_send_commands(commands=commands, with_output=True, wait_before_output=0.01, wait_between_commands=0.01)

    regex_pattern = r'(?<=demangle is: )(.*)'
    output_ = re.findall(regex_pattern, ssh.full_output)
    if output_:
        output_ = output_[-1].replace('\r', '').replace('\n', '')
        # print(f'\n{output_}')
    else:
        output_ = None
        print('\nThere is no demangle')

    return output_


def main():
    ssh = SSHConnection(
        # ip_address='172.20.63.185',
        ip_address='172.20.62.17',
        username='spuser',
        password='sp_user9'
    )
    ssh.ssh_connection()
    commands = [
        'python3',
        'import cxxfilt',
        'from ctypes.util import find_library',
    ]
    ssh.ssh_send_commands(commands=commands, with_output=False, wait_before_output=0.01, wait_between_commands=0.01)

    #

    ssh.full_output = ''
    bt_mangle_list = [
        '_Z14SigDumpHandleriP9siginfo_tPv',
        '_ZN22ProcessSubscriberSpace12PsAggregator14handleResponseEP8CLI_CMD_P13CLI_ERR_CODE_jPv',
        '0x24d',
    ]
    demangle_output_dict = {
        bt_mangle: get_demangle(ssh, bt_mangle) for bt_mangle in bt_mangle_list
    }

    xxx = ' -> '.join(bt_mangle_list)
    print(xxx)

    xxx = ' -> '.join([demangle_output_dict[v] for v in bt_mangle_list if v in list(demangle_output_dict.keys())])
    print(xxx)

    print()


if __name__ == '__main__':
    main()
