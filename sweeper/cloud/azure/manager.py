__author__ = 'fer'

import base64
import time

from azure.servicemanagement import *

from sweeper.resource import Resource, ResourceConfig
from sweeper.resource import generate_random_password
from sweeper.cloud.azure.subscription import sms


def create_resource(name):
    res = Resource(name, '{0}.cloudapp.net', 'azureuser', generate_random_password())

    # Service Certificate
    cert_encoded = encode_certificate('mycert.pem')

    # Key to password-less login
    vm_key_fingerprint = '976272116B6DE9398D1032C85B69CD6E6638F691' #mycert.pem
    linux_config = LinuxConfigurationSet(res.name, res.defaultUser, res.defaultPassword, True)
    key_pair = KeyPair(vm_key_fingerprint, '/home/{0}/id_rsa'.format(res.defaultUser))
    public_key = PublicKey(vm_key_fingerprint, '/home/{0}/.ssh/authorized_keys'.format(res.defaultUser))
    linux_config.ssh.public_keys.public_keys.append(public_key)
    linux_config.ssh.key_pairs.key_pairs.append(key_pair)
    linux_config.disable_ssh_password_authentication = False

    # Virtual Hard Disk
    # TODO: Automate configuration of storage account
    image_name = '0b11de9248dd4d87b18621318e037d37__RightImage-Ubuntu-14.04-x64-v14.2'
    media_link = 'https://sweepervhd.blob.core.windows.net/vmblob/{0}.vhd'.format(res.name)
    os_hd = OSVirtualHardDisk(image_name, media_link)

    # Network configuration (SSH endpoints)
    net_cfg = create_network_config()

    # Service Creation
    sms.create_hosted_service(service_name=res.name,
                              label=res.name,
                              description='Cloud service for VM {0}'.format(res.name),
                              location='East US')  # TODO: remove location hardcoded

    time.sleep(10)

    # Add certificate to service
    sms.add_service_certificate(service_name=res.name,
                                data=cert_encoded,
                                certificate_format='pfx',
                                password='')

    time.sleep(3)

    # Virtual machine creation
    sms.create_virtual_machine_deployment(service_name=res.name,
                                          deployment_name=res.name,
                                          deployment_slot='production',
                                          label=res.name,
                                          role_name=res.name,
                                          system_config=linux_config,
                                          os_virtual_hard_disk=os_hd,
                                          role_size='Small',
                                          network_config=net_cfg)

    time.sleep(10)

    return res


def encode_certificate(cer_file):
    with open(cer_file, 'rb') as cer_file:
        encoded_cer = base64.b64encode(cer_file.read())

    return encoded_cer


def create_network_config(subnet_name=None):
    network = ConfigurationSet()
    network.configuration_set_type = 'NetworkConfiguration'
    network.input_endpoints.input_endpoints.append(
        ConfigurationSetInputEndpoint('SSH', 'tcp', '22', '22'))
    if subnet_name:
        network.subnet_names.append(subnet_name)

    return network


def possible_configs(num):
    result = sms.list_role_sizes()
    result = [x for x in result.role_sizes if x.name in ['ExtraLarge', 'ExtraSmall', 'Large', 'Medium', 'Small']]
    cfgs = [ResourceConfig(o.name, o.cores, o.memory_in_mb) for o in result]

    combinations = []
    #knackspack via cores
    def compute_combinations(num_req, config_list, res_list, idx):
        if num_req == 0:
            combinations.append(list(config_list))
        else:
            for i in range(idx, len(res_list)):
                cfg = res_list[i]
                if num_req - cfg.cores >= 0:
                    config_list.append(cfg)
                    compute_combinations(num_req - cfg.cores, config_list, res_list, i)
                    config_list.pop()

    compute_combinations(num, [], cfgs, 0)

    return combinations