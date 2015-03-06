from paramiko import SSHClient
import random


class Resource:
    def __init__(self, name, hostname, user, passwd):
        self.name = name
        self.hostname = hostname
        self.defaultUser = user
        self.defaultPassword = passwd
        self.ssh = SSHClient()

    def connect_ssh(self):
        self.ssh.connect(hostname=self.hostname,
                         username=self.defaultUser,
                         password=self.defaultPassword,
                         # key_filename='mycert.pem',
                         look_for_keys=False)

    def execute_command(self, cmd):
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        return stdin, stdout, stderr

    def __del__(self):
        self.ssh.close()


def generate_random_password():
    # Secure cryptographic random
    rnd = random.SystemRandom()
    len_k = rnd.randint(8, 15)
    keyword = '#' * len_k

    for i in range(len_k):
        num = rnd.randint(1, 3)
        if num == 1:    # generate number
            x = rnd.randint(ord('0'), ord('9'))
        elif num == 2:  # generate lowercase
            x = rnd.randint(ord('a'), ord('z'))
        elif num == 3:  # generate uppercase
            x = rnd.randint(ord('A'), ord('Z'))
        keyword[i] = chr(x)

    return keyword