#!/usr/bin/python3


from paramiko import SSHClient
import paramiko
from scp import SCPClient


if __name__ == '__main__':
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #TODO: Connect via .pem fiile
    ssh.connect(hostname='whitestarvm.cloudapp.net',
                username='azureuser',
                password='Balataraybestos4',
                #key_filename='mycert.pem',
                look_for_keys=False)


    # TODO: where does it connect?
    scp = SCPClient(ssh.get_transport())

    scp.put('azure_os_linux.txt', 'os_list.txt')
    scp.get(remote_path='os_list.txt', local_path='.')
