#!/usr/bin/python3

__author__ = '@dominofire'


from paramiko import SSHClient
import paramiko
import sys


if __name__ == '__main__':
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #TODO: Connect via .pem fiile

    ssh.connect(hostname='whitestarvm.cloudapp.net',
                username='azureuser',
                password='Balataraybestos4',
                #key_filename='mycert.pem',
                look_for_keys=False)

    # Aqui esperamos
    stdin, stdout, stderr = ssh.exec_command('ls -al')

    for line in stdout:
        sys.stdout.write(line)

    for line in stderr:
        sys.stdout.write(line)

    # for line in stdin:
    #     sys.stdout.write(line)
