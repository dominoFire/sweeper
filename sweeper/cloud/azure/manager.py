from azure.storage import BlobService

import base64
import logging
from azure.servicemanagement import *
from azure.storage.fileshareservice import FileShareService

from sweeper.resource import Resource, ResourceConfig, generate_valid_ramdom_password
from sweeper.cloud.azure.subscription import sms
from sweeper.cloud.azure.subscription import pfx_fullpath, cer_fullpath
import sweeper.utils as utils
import sweeper.cloud.azure.resource_config_factory as config_factory


def filter_any_hosted_service(svc_name):
    return utils.filter_any(lambda x: x.service_name == svc_name, sms.list_hosted_services().hosted_services)


def wait_for_hosted_service(service_name):
    utils.wait_for(filter_any_hosted_service, svc_name=service_name)


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
    def status_succeeded():
        st = sms.get_operation_status(request_id=request_id)
        if st.status == 'Succeeded':
            return True
        elif st.status == 'Failed':
            print(st.http_status_code, st.error.code, st.error.message)
            raise ValueError('Request status failed: {0}'.format(st.error.message))
        return False

    utils.wait_for(status_succeeded)


def wait_for_deployment_running(service_name, deploy_name):
    wait = True
    while wait:
        st = sms.get_deployment_by_name(service_name, deploy_name)
        if st.status == 'Running':
            wait = False
            break


def filter_any_storage_account(stor_account):
    return utils.filter_any(lambda x: x.service_name == stor_account, sms.list_storage_accounts().storage_services)


def wait_for_storage_account(storage_name):
    utils.wait_for(filter_any_storage_account, stor_account=storage_name)


def get_media_link(storage_account_name, container_name, file_name):
    return 'https://{0}.blob.core.windows.net/{1}/{2}'.format(storage_account_name, container_name, file_name)


def create_resource(name, config_object):
    """
    Creates a virtual machine
    :param name:
    :param config_object:
    :return: a Resource object that represents the virtual machine
    """
    res = Resource(config_object, name, '{0}.cloudapp.net'.format(name), 'azureuser', generate_valid_ramdom_password())

    # Service Certificate
    # TODO: parametrize .cer management
    cert_encoded = encode_certificate(cer_fullpath)

    # Key to password-less login
    vm_key_fingerprint = '97C186F85ED3A86959AECD0845C5A2BFBFB9B6E5'  # mycert.pem
    linux_config = LinuxConfigurationSet(res.name, res.defaultUser, res.defaultPassword, True)
    key_pair = KeyPair(vm_key_fingerprint, '/home/{0}/id_rsa'.format(res.defaultUser))
    public_key = PublicKey(vm_key_fingerprint, '/home/{0}/.ssh/authorized_keys'.format(res.defaultUser))
    linux_config.ssh.public_keys.public_keys.append(public_key)
    linux_config.ssh.key_pairs.key_pairs.append(key_pair)
    linux_config.disable_ssh_password_authentication = False

    # OS Image
    # TODO: Automate configuration of image
    image_name = 'b39f27a8b8c64d52b05eac6a62ebad85__Ubuntu-14_04_2_LTS-amd64-server-20150309-en-us-30GB'

    # Storage account
    logging.info('Creating Storage account {0}'.format(res.name))
    storage_account_result = sms.create_storage_account(service_name=res.name,
                                                        description='Storage account for VM {}'.format(res.name),
                                                        label=res.name,
                                                        geo_replication_enabled=None,
                                                        account_type='Standard_LRS',
                                                        location='West US')   # TODO: remove location hardcoded
    wait_for_request_succeeded(storage_account_result.request_id)
    wait_for_storage_account(res.name)
    logging.info('Creating Storage account {0} complete'.format(res.name))

    # Container for VHD images
    container_name = 'vhd'
    logging.info('Creating Container \'{0}\' in Storage account {1}'.format(container_name, res.name))
    storage_keys = sms.get_storage_account_keys(service_name=res.name)
    blob_svc = BlobService(account_name=res.name, account_key=storage_keys.storage_service_keys.primary)
    file_svc = FileShareService(account_name=res.name, account_key=storage_keys.storage_service_keys.primary)
    blob_svc.create_container(container_name)
    file_svc.create_file_share('fileshare')
    logging.info('Creating Container {0} in Storage account {1} complete'.format(container_name, res.name))

    vhd_link = get_media_link(res.name, container_name, '{0}.vhd'.format(res.name))
    logging.info('VHD link: {0}'.format(vhd_link))
    os_hd = OSVirtualHardDisk(image_name, vhd_link)

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
                                data=cert_encoded.decode('utf-8'),
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
                                                      role_size=config_object.config_name,
                                                      network_config=net_cfg)
    #wait_for_deployment(res.name, res.name)
    wait_for_request_succeeded(vm_result.request_id)
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
    configs = config_factory.list_configs()

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
    # Check if servie exists
    svc = sms.get_hosted_service_properties(res_name)
    if not svc:
        raise ValueError('Service {0} not found'.format(res_name))
    # Turn off Virtual Machine
    shutdown_result = sms.shutdown_role(service_name=res_name,
                                        deployment_name=res_name,
                                        role_name=res_name,
                                        post_shutdown_action='StoppedDeallocated')
    wait_for_request_succeeded(shutdown_result.request_id)
    # Delete additional deployments
    if svc.deployments:
        for d in svc.deployments:
            logging.info('Deleting deployment {0}:{1}'.format(svc.service_name, d.name))
            req = sms.delete_deployment(svc.service_name, d.name)
            wait_for_request_succeeded(req.request_id)
            logging.info('Deleting deployment {0}:{1} complete'.format(svc.service_name, d.name))

    #TODO: Find out how to delete all deployments
    def get_deployment():
        try:
            return sms.get_deployment_by_name(res_name, res_name)
        except Exception as e:
            return None

    if get_deployment():
        logging.info('Deleting default deployment {0}'.format(res_name))
        req = sms.delete_deployment(res_name, res_name)
        wait_for_request_succeeded(req.request_id)
        logging.info('Deleting default deployment {0} complete'.format(res_name))

    def get_role():
        try:
            return sms.get_role(service_name=res_name, deployment_name=res_name, role_name=res_name)
        except Exception as e:
            return None

    # Delete Virtual machine role after deployments!
    if get_role():
        delete_result = sms.delete_role(service_name=res_name,
                                        deployment_name=res_name,
                                        role_name=res_name)
        wait_for_request_succeeded(delete_result.request_id)

    logging.info('Deleting cloud service {0}'.format(res_name))
    sms.delete_hosted_service(res_name)
    utils.wait_for(lambda x: not filter_any_hosted_service(x), x=res_name)
    logging.info('Deleting cloud service {0} complete'.format(res_name))

    #logging.info('Deleting Storage account {0}'.format(res_name))
    #sms.delete_storage_account(res_name)
    #logging.info('Deleting Storage account {0} complete'.format(res_name))
