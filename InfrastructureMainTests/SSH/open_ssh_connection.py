from InfrastructureSVG.Network_Infrastructure.SSH_Infrastructure import SSHConnection

if __name__ == '__main__':
    ssh = SSHConnection(
        ip_address='asil-mg',
        username='administrator',
        password='sp_user9'
    )
    ssh.ssh_connection()
    #

    commands = ['ifconfig']
    ssh.ssh_send_commands(commands=commands, with_output=True)
    # print(ssh.last_session_output)
    print(ssh.full_output)

    #
    ssh.ssh_close_connection()
    print()
