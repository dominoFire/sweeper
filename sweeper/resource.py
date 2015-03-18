from paramiko import SSHClient
import random


class Resource:
    def __init__(self, name, hostname, user, passwd):
        self.name = name
        self.hostname = hostname
        self.defaultUser = user
        self.defaultPassword = passwd
        self.ssh = SSHClient()
        self.speed_factor = 1

    def connect_ssh(self):
        # For some reason, I can't connect using a SSH certificate
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


class ResourceConfig:
    def __init__(self, name, cores, ram_memory):
        self.config_name = name
        self.cores = cores
        self.ram_memory = ram_memory

    def __str__(self):
        return '{0}({1},{2})'.format(self.config_name, self.cores, self.ram_memory)

    def __repr__(self):
        return self.__str__()


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
