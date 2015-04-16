from paramiko import SSHClient
from scp import SCPClient
import random
import paramiko
import logging


class Resource:
    """
    Represents a full, stateful Virtual Machine object that can execute commands
    """

    def __init__(self, res_config, name, hostname, user, passwd, keep_ssh_alive=True):
        self.res_config = res_config
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
        except Exception as e:
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
        except Exception as ex:
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
    """
    Represents a possible Virtual Machine configuration. It doesn't take into account
    region issues
    """

    def __init__(self, name, cores, ram_memory, provider, speed_factor, cost_hour_usd):
        self.config_name = name
        """ VM configuration name """
        self.cores = cores
        """ Number of cores in the VM configuration """
        self.ram_memory = ram_memory
        """ Amount of RAM memory in MegaBytes in the VM configuration """
        self.provider = provider
        """ Name of the cloud provider (Azure, AWS, Rackspace, ...) that supports this configuration """
        self.speed_factor = speed_factor
        """ The SPECfp score of this configuration """
        self.cost_hour_usd = cost_hour_usd
        """ The cost of running this virtual machine during an hour, in US Dollars.
            Note that hour fractions shouldn't be charged by the cloud provider """

    def __str__(self):
        return '{0}({1},{2})'.format(self.config_name, self.cores, self.ram_memory)

    def __repr__(self):
        return self.__str__()


def generate_random_password():
    """
    Generates a random password for using in VM user authentication
    :return:
    """
    # Secure cryptographic random
    rnd = random.SystemRandom()
    len_k = rnd.randint(8, 15)
    keyword = []

    for i in range(len_k):
        num = rnd.randint(1, 3)
        if num == 1:  # generate number
            x = rnd.randint(ord('0'), ord('9'))
        elif num == 2:  # generate lowercase
            x = rnd.randint(ord('a'), ord('z'))
        elif num == 3:  # generate uppercase
            x = rnd.randint(ord('A'), ord('Z'))
        keyword.append(chr(x))

    keyword = ''.join(keyword)

    return keyword


def validate_password_requirements(passwd):
    """
    Check if :passwd approves the following password complexity requirements

    - at least 8 characters
    - 3 of the following conditions
       - at least 1 lowercase char
       - at least 1 uppercase char
       - at least 1 number char
       - at least 1 special (not alphanumeric) char

    :return: True if complies with password complexity requirements
    """
    if not len(passwd) >= 8:
        return False

    req_lower = False
    req_upper = False
    req_digit = False
    req_special_char = False
    for ch in passwd:
        if str.isupper(ch):
            req_upper = True
        elif str.islower(ch):
            req_lower = True
        elif str.isdigit(ch):
            req_digit = True
        # See
        #http://azure.microsoft.com/en-us/documentation/articles/virtual-machines-docker-with-xplat-cli/
        elif ch in '!@#$%^&+=':
            req_special_char = True

    return int(req_upper) + int(req_lower) + int(req_digit) + int(req_special_char) >= 3


def generate_valid_ramdom_password():
    p = generate_random_password()
    while not validate_password_requirements(p):
        p = generate_random_password()

    return p
