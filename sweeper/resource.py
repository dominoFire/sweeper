from paramiko import SSHClient
from scp import SCPClient
import logging
import paramiko


class Resource:
    """
    Represents a Virtual Machine object that can execute commands. This class
    is used to encapsulate all the complexities used
    """

    def __init__(self, res_config, name, hostname, user, passwd):
        self.res_config = res_config
        """ ResourceConfig object that originates this resource """
        self.name = name
        """ Name of the resource """
        self.hostname = hostname
        """ Hostname used to connect to thw VM """
        self.defaultUser = user
        """ Username to connect to the base Virtual Machine """
        self.defaultPassword = passwd
        """  TODO: Find a better way to store passwords """
        self.speed_factor = res_config.speed_factor
        """ A score that ranks how fast is this base Virtual Machine resource """

    def create_ssh_client(self):
        """
        Creates a paramiko SSHClient object with guaranteed connection the cloud resource

        :return: A :class:`paramiko.SSHClient` object
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
                logging.debug('Can\'t connect SSH: {0}'.format(ssh_ex))

        return client

    def execute_command(self, cmd, working_dir='~'):
        """
        Creates a paramiko SSHClient and invokes execution of a terminal command.

        :param str cmd: Command to execute in the VM resource
        :param str working_dir: Working-directory used to execute the command
        :return: a tuple of the form (stdin, stdout, stderr, client)
        """
        ssh = self.create_ssh_client()
        stdin, stdout, stderr = ssh.exec_command('cd {} && {}'.format(working_dir, cmd))
        return stdin, stdout, stderr, ssh

    def put_file(self, local_filepath, remote_filepath):
        """
        Upload a file from the host machine to the VM resource

        :param str local_filepath: Filepath in the local machine of the file to upload to DFS
        :param str remote_filepath: Destination filepath of the file in the DFS
        :returns: ::None
        """
        ssh = self.create_ssh_client()
        scp = SCPClient(ssh.get_transport())
        scp.put(local_filepath, remote_filepath)
        ssh.close()
        return None

    def get_file(self, remote_filepath, curr_filepath='.'):
        """
        Download a file from the VM resource to the host machine

        :param str remote_filepath: Source filepath of the file in the DFS
        :param str local_filepath: Destination Filepath in the local machine of the file
        """
        ssh = self.create_ssh_client()
        scp = SCPClient(ssh.get_transport())
        scp.get(remote_filepath, local_path=curr_filepath)
        ssh.close()
        return None


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
        """ Name of the cloud base (Azure, AWS, Rackspace, ...) that supports this configuration """
        self.speed_factor = speed_factor
        """ The SPECfp score of this configuration """
        self.cost_hour_usd = cost_hour_usd
        """ The cost of running this virtual machine during an hour, in US Dollars.
            Note that hour fractions shouldn't be charged by the cloud base """

    def __str__(self):
        return '{0}({1},{2})'.format(self.config_name, self.cores, self.ram_memory)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, ResourceConfig):
            return False
        return self.config_name == other.config_name and self.provider == other.provider

    def __hash__(self):
        return str(self.config_name + self.provider).__hash__()
