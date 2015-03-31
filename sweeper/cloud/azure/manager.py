__author__ = 'fer'

import base64
import logging
from azure.servicemanagement import *

from sweeper.resource import Resource, ResourceConfig
from sweeper.resource import generate_random_password
from sweeper.cloud.azure.subscription import sms
from sweeper.cloud.azure.subscription import cer_fullpath


def wait_for_hosted_service(service_name):
    wait = True
    while wait:
        hs = sms.list_hosted_services()
        for s in hs.hosted_services:
            if s.service_name == service_name:
                wait = False
                break


def wait_for_deployment(service_name, deploy_name):
    wait = True
    while wait:
        svc = sms.get_hosted_service_properties(service_name)
        if not svc:
            raise ValueError('No service {0}'.format(service_name))
        if svc.deployments:
            for d in svc.deployments:
                if d.name == deploy_name:
                    wait = False
                    break
        else:
            raise ValueError('No deployments in service {0}'.format(service_name))


def wait_for_service_certificate(service_name, cert_fingerprint):
    wait = True
    while wait:
        sc = sms.list_service_certificates(service_name)
        for s in sc.certificates:
            if s.thumbprint == cert_fingerprint:
                wait = False
                break


def wait_for_request_succeeded(request_id):
    wait = True
    while wait:
        st = sms.get_operation_status(request_id=request_id)
        if st.status == 'Succeeded':
            wait = False
            break


def wait_for_deployment_running(service_name, deploy_name):
    wait = True
    while wait:
        st = sms.get_deployment_by_name(service_name, deploy_name)
        if st.status == 'Running':
            wait = False
            break


def create_resource(name):
    res = Resource(name, '{0}.cloudapp.net'.format(name), 'azureuser', generate_random_password())

    # Service Certificate
    # TODO: parametrize this
    cert_encoded = encode_certificate(cer_fullpath)

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
    image_name = 'b39f27a8b8c64d52b05eac6a62ebad85__Ubuntu-14_04_2_LTS-amd64-server-20150309-en-us-30GB'
    media_link = 'https://sweepervhd.blob.core.windows.net/vmblob/{0}.vhd'.format(res.name)
    os_hd = OSVirtualHardDisk(image_name, media_link)

    # Network configuration (SSH endpoints)
    net_cfg = create_network_config()

    # Service Creation
    logging.info('Creating Hosted service {0} started'.format(res.name))
    sms.create_hosted_service(service_name=res.name,
                              label=res.name,
                              description='Cloud service for VM {0}'.format(res.name),
                              location='West US')  # TODO: remove location hardcoded
    wait_for_hosted_service(res.name)
    logging.info('Creating Hosted service {0} completed'.format(res.name))

    # Add certificate to service
    logging.info('Adding service certificate for {0}'.format(res.name))
    sms.add_service_certificate(service_name=res.name,
                                data=cert_encoded,
                                certificate_format='pfx',
                                password='')
    wait_for_service_certificate(res.name, vm_key_fingerprint)
    logging.info('Adding service certificate for {0} complete'.format(res.name))


    # Virtual machine creation
    logging.info('Creating VM deployment {0}'.format(res.name))
    vm_result = sms.create_virtual_machine_deployment(service_name=res.name,
                                                      deployment_name=res.name,
                                                      deployment_slot='production',
                                                      label=res.name,
                                                      role_name=res.name,
                                                      system_config=linux_config,
                                                      os_virtual_hard_disk=os_hd,
                                                      role_size='Small',
                                                      network_config=net_cfg)
    #wait_for_deployment(res.name, res.name)
    wait_for_deployment_running(res.name, res.name)
    logging.info('Creating VM deployment {0} complete'.format(res.name))

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
    result = result.role_sizes
    configs = [ResourceConfig(o.name, o.cores, o.memory_in_mb) for o in result]

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

    compute_combinations(num, [], configs, 0)

    return combinations


def delete_resource(res_name):
    svc = sms.get_hosted_service_properties(res_name)
    if not svc:
        raise ValueError('Service {0} not found'.format(res_name))
    if svc.deployments:
        for d in svc.deployments:
            logging.info('Deleting deployment {0}:{1}'.format(svc.service_name, d.name))
            req = sms.delete_deployment(svc.service_name, d.name)
            wait_for_request_succeeded(req.request_id)
            logging.info('Deleting deployment {0}:{1} complete'.format(svc.service_name, d.name))

    #TODO: Find out how to delete all deployments

    logging.info('Deleting default deployment {0}'.format(res_name))
    req = sms.delete_deployment(res_name, res_name)
    wait_for_request_succeeded(req.request_id)
    logging.info('Deleting default deployment {0} complete'.format(res_name))

    logging.info('Deleting cloud service {0}'.format(res_name))
    sms.delete_hosted_service(svc.service_name)
    logging.info('Deleting cloud service {0} complete'.format(res_name))
