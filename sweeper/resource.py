from paramiko import SSHClient
from scp import SCPClient
import random
import paramiko
import logging

class Resource:
    def __init__(self, name, hostname, user, passwd, keep_ssh_alive=True):
        self.name = name
        self.hostname = hostname
        self.defaultUser = user
        self.defaultPassword = passwd
        self.__ssh = None
        self.__scp = None
        self.is_ssh_connected = True
        self.keep_ssh_alive = keep_ssh_alive
        self.speed_factor = 1

    def connect_ssh(self):
        # For some reason, I can't connect using a SSH certificate
        try:
            if self.__ssh is None:
                self.__ssh = SSHClient()
                self.__ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.__ssh.connect(hostname=self.hostname,
                               username=self.defaultUser,
                               password=self.defaultPassword,
                               # key_filename='mycert.pem',
                               look_for_keys=False)
            self.is_ssh_connected = True
        except Exception, e:
            logging.warning('Cant connect SSH: {0}'.format(e))
            self.__ssh = None
            self.is_ssh_connected = False
        finally:
            return self.is_ssh_connected

    def disconnect_ssh(self):
        if not self.keep_ssh_alive:
            self.__ssh.close()
            self.__ssh = None
            self.is_ssh_connected = False
        pass

    def connect_scp(self):
        try:
            if not self.is_ssh_connected:
                self.connect_ssh()
            if self.__scp is None:
                self.__scp = SCPClient(self.__ssh.get_transport())
        except:
            self.__scp = None

    def execute_command(self, cmd):
        self.connect_ssh()
        stdin, stdout, stderr = self.__ssh.exec_command(cmd)
        self.disconnect_ssh()

        return stdin, stdout, stderr

    def put_file(self, local_filepath, remote_filepath):
        self.connect_scp()
        self.__scp.put(local_filepath, remote_filepath)
        self.disconnect_ssh()

    def get_file(self, remote_filepath, curr_filepath='.'):
        self.connect_scp()
        self.__scp.get(remote_filepath, local_path=curr_filepath)
        self.disconnect_ssh()

    def __del__(self):
        if self.__ssh:
            self.__ssh.close()


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
    keyword = []

    for i in range(len_k):
        num = rnd.randint(1, 3)
        if num == 1:    # generate number
            x = rnd.randint(ord('0'), ord('9'))
        elif num == 2:  # generate lowercase
            x = rnd.randint(ord('a'), ord('z'))
        elif num == 3:  # generate uppercase
            x = rnd.randint(ord('A'), ord('Z'))
        keyword.append(chr(x))

    keyword = ''.join(keyword)

    return keyword
