__author__ = '@dominofire'

from paramiko import SSHClient
from scp import SCPClient
import logging
import paramiko


class Resource:
    """
    Represents a Virtual Machine object that can execute commands
    """

    def __init__(self, res_config, name, hostname, user, passwd):
        self.res_config = res_config
        self.name = name
        self.hostname = hostname
        self.defaultUser = user
        self.defaultPassword = passwd
        self.speed_factor = res_config.speed_factor

    def create_ssh_client(self):
        """
        Creates a paramiko SShClient object with guaranteed connection
        :return:
        """
        # For some reason, I can't connect using a SSH certificate
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        not_connected = True
        logging.debug('Creating SSHClient')
        while not_connected:
            try:
                client.connect(hostname=self.hostname,
                               username=self.defaultUser,
                               password=self.defaultPassword,
                               # key_filename='mycert.pem',
                               look_for_keys=False)
                not_connected = False
                logging.debug('Created SSHClient')
            except Exception as ssh_ex:
                logging.debug('Cant connect SSH: {0}'.format(ssh_ex))

        return client

    def execute_command(self, cmd, working_dir='~'):
        """
        Creates a paramiko SSHClient and invokes execution of a terminal command.
        :param cmd str Command to execute in the VM resource
        :returns a tuple of the form (stdin, stdout, stderr, client)
        """
        ssh = self.create_ssh_client()
        stdin, stdout, stderr = ssh.exec_command('cd {} && {}'.format(working_dir, cmd))
        return stdin, stdout, stderr, ssh

    def put_file(self, local_filepath, remote_filepath):
        """
        Upload a file from the host machine to the VM resource
        """
        ssh = self.create_ssh_client()
        scp = SCPClient(ssh.get_transport())
        scp.put(local_filepath, remote_filepath)
        ssh.close()

    def get_file(self, remote_filepath, curr_filepath='.'):
        """
        Download a file from the VM resource to the host machine
        """
        ssh = self.create_ssh_client()
        scp = SCPClient(ssh.get_transport())
        scp.get(remote_filepath, local_path=curr_filepath)
        ssh.close()


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
