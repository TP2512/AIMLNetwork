from InfrastructureSVG.Network_Infrastructure.SSH_Infrastructure import SSHConnection
import socket

if __name__ == '__main__':
    ssh = SSHConnection(
        ip_address='asil-mg',
        username='administrator',
        password='sp_user9'
    )
    ssh.ssh_connection()

    ssh.ssh_close_connection()

    try:
        ssh.remote_ssh.send('ifconfig\n')
    except socket.error as err:
        print(err)
        print()
    except Exception as err:
        print(err)
        print()

    print()
