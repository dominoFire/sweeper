from paramiko import SSHClient
from scp import SCPClient
from subprocess import CalledProcessError

import logging
import os
import paramiko
import subprocess
import sys

class Resource:
    """
    Represents a Virtual Machine object that can execute commands. This class
    is used to encapsulate all the complexities when we're dealing
    with Virtual Machines over all possible providers 
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
        self.ssh_public_key_path = None
        """ Filepath to local service where the public key resides """
        self.ssh_private_key_path = None
        """ Filepath in local service where the private key resides """
        self.ssh_fingerprint = None
        """ Fingerprint of the OpenSSH-formated public key """

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


    def generate_ssh_keys(self):
        """
        Generates an OpenSSH file
        Saves the expected variables
        """
        base_path = os.path.join('.', 'cluster_data', self.name)
        self.ssh_private_key_path = os.path.join(base_path, 'login_key')
        self.ssh_public_key_path = os.path.join(base_path, 'login_key.pub')

        if not os.path.exists(base_path):
            os.makedirs(base_path)
        
        cmd_private = ["ssh-keygen", "-q", "-N", "", "-f", self.ssh_private_key_path]
        try:
            subprocess.run(cmd_private, check=True)
        except CalledProcessError as e:
            logging.error("Error al generar llave privdada SSH: {}", str(e))
            raise e

        cmd_finger = ["ssh-keygen", "-lf", self.ssh_private_key_path, "-E", "md5"]
        try:
            out_b = subprocess.check_output(cmd_finger)
            # TODO: esto es system-dependent ?
            out = out_b.decode('UTF-8')
            # Esperemos no cambie
            out_list = out.split(" ")
            # La primera parte dice "MD5"
            finger_list = out_list[1].split(":")[1:]
            self.ssh_fingerprint = ''.join(finger_list).upper()
        except CalledProcessError as e:
            logging.error("Error al obtener SSH fingerprint: {}", str(e))
            raise e

        # Esto no funciona por un bug en pycrypto
        # key = RSA.generate(2048)
        # pubkey = key.publickey()
        # self.ssh_fingerprint = MD5.new(key.exportKey('DER')).hexdigest().upper()
        # logging.info("Fingerprint: {}".format(self.ssh_fingerprint))

        # with os.fdopen(os.open(self.ssh_private_key_path, os.O_WRONLY | os.O_CREAT, 0o600), 'wb') as fh:
        #     fh.write(key.exportKey('PEM'))

        # with os.fdopen(os.open(self.ssh_public_key_path, os.O_WRONLY | os.O_CREAT, 0o600), 'wb') as fh:
        #     #fh.write(pubkey.exportKey('OpenSSH'))
        #     tt = pubkey.exportKey('OpenSSH')
        #     print(tt)
        #     print(type(tt))
        

    def generate_certificates(self):
        base_path = os.path.join('.', 'cluster_data', self.name)
        self.csr_path = os.path.join(base_path, 'certifcate.csr')
        self.cer_path = os.path.join(base_path, 'certifcate.cer')
        
        subj = "/C=MX/ST=Mexico City/L=Mexico City/O=pulsarcloud/CN={}".format(self.name)
        cmd_csr = ["openssl", "req", "-x509", "-days", "365", "-new", "-key", self.ssh_private_key_path, "-out", self.csr_path, "-subj", subj]
        try:
            subprocess.run(cmd_csr, check=True)
        except CalledProcessError as e:
            logging.error("Error al generar OpenSSL CSR: {}", str(e))
            raise e
        
        cmd_cer = ["openssl", "x509", "-inform", "pem", "-in", self.csr_path, "-outform", "der", "-out", self.cer_path]
        try:
            subprocess.run(cmd_cer, check=True)
        except CalledProcessError as e:
            logging.error("Error al generar OpenSSL CER: {}", str(e))
            raise e


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
