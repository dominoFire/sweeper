import base64
import logging
import random
import sweeper.utils as utils
import uuid

from azure.storage import BlobService
from azure.servicemanagement import *
from azure.storage.fileshareservice import FileShareService
from sweeper.resource import Resource, ResourceConfig


def filter_any_hosted_service(sms, svc_name):
    return utils.filter_any(lambda x: x.service_name == svc_name, sms.list_hosted_services().hosted_services)


def wait_for_hosted_service(sms, service_name):
    utils.wait_for(filter_any_hosted_service, sms=sms, svc_name=service_name)


def wait_for_deployment(sms, service_name, deploy_name):
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


def wait_for_service_certificate(sms, service_name, cert_fingerprint):
    wait = True
    while wait:
        sc = sms.list_service_certificates(service_name)
        for s in sc.certificates:
            if s.thumbprint == cert_fingerprint:
                wait = False
                break


def wait_for_request_succeeded(sms, request_id):
    def status_succeeded():
        st = sms.get_operation_status(request_id=request_id)
        if st.status == 'Succeeded':
            return True
        elif st.status == 'Failed':
            print(st.http_status_code, st.error.code, st.error.message)
            raise ValueError('Request status failed: {0}'.format(st.error.message))
        return False

    utils.wait_for(status_succeeded)


def wait_for_deployment_running(sms, service_name, deploy_name):
    wait = True
    while wait:
        st = sms.get_deployment_by_name(service_name, deploy_name)
        if st.status == 'Running':
            wait = False
            break


def filter_any_storage_account(sms, stor_account):
    return utils.filter_any(lambda x: x.service_name == stor_account, sms.list_storage_accounts().storage_services)


def wait_for_storage_account(sms, storage_name):
    utils.wait_for(filter_any_storage_account, sms=sms, stor_account=storage_name)


def get_media_link(storage_account_name, container_name, file_name):
    return 'https://{0}.blob.core.windows.net/{1}/{2}'.format(storage_account_name, container_name, file_name)


def create_resource(sms, name, config_object):
    """
    Creates a virtual machine
    :param name:
    :param config_object:
    :return: a Resource object that represents the virtual machine
    """
    res = Resource(config_object, name, '{0}.cloudapp.net'.format(name), 'azureuser', generate_valid_ramdom_password())

    # Service Certificate
    # TODO: parametrize .cer management
    cert_encoded = encode_certificate(config_object.service_certificate_path)

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
    storage_keys = create_storage_account(sms, res.name)

    # Container for VHD image for VM
    container_name = 'vhd'
    create_container(res.name, 'vhd', storage_keys)

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
    wait_for_hosted_service(sms, res.name)
    logging.info('Creating Hosted service {0} completed'.format(res.name))

    # Add certificate to service
    logging.info('Adding service certificate for {0}'.format(res.name))
    sms.add_service_certificate(service_name=res.name,
                                data=cert_encoded.decode('utf-8'),
                                certificate_format='cer',
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


def delete_resource(sms, res_name):
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


def create_distributed_file_system(storage_account, fileshare):
    """
    Creates a Azure Storage account and a file share that can work as a
    Distributed Filesystem across Azure VM's
    :param storage_account:
    :param fileshare:
    :return: Storage keys for further access
    """
    storage_keys = create_storage_account(sms, storage_account)
    create_fileshare(storage_account, fileshare, storage_keys)
    return storage_keys


def create_storage_account(sms, name):
    """
    Creates a storage account in Microsoft Azure subscription and return its access keys
    :param name:
    :return:
    """
    logging.info('Creating Storage account {0}'.format(name))
    storage_account_result = sms.create_storage_account(service_name=name,
                                                        description='Sweeper managed storage account',
                                                        label=name,
                                                        geo_replication_enabled=None,
                                                        account_type='Standard_LRS',
                                                        location='West US')   # TODO: remove location hardcoded
    wait_for_request_succeeded(sms, storage_account_result.request_id)
    wait_for_storage_account(sms, name)
    logging.info('Creating Storage account {0} complete'.format(name))

    storage_keys = sms.get_storage_account_keys(service_name=name)

    return storage_keys


def create_fileshare(storage_account_name, fileshare_name, storage_keys):
    """
    Creates a file share in the specified Microsoft Azure Storage account
    :param storage_account_name:
    :param fileshare_name:
    :param storage_keys:
    :return:
    """
    logging.info('Creating Fileshare \'{0}\' in Storage account {1}'.format(fileshare_name, storage_account_name))
    file_svc = FileShareService(account_name=storage_account_name, account_key=storage_keys.storage_service_keys.primary)
    file_svc.create_file_share(fileshare_name)
    logging.info('Creating Fileshare \'{0}\' in Storage account {1} complete'.format(fileshare_name, storage_account_name))


def create_container(storage_account_name, container_name, storage_keys):
    """
    Creates a file share in the specified Microsoft Azure Storage account.
    A container is like a folder within a storage account
    :param storage_account_name:
    :param container_name:
    :param storage_keys:
    :return:
    """
    logging.info('Creating Container \'{0}\' in Storage account {1}'.format(container_name, storage_account_name))
    blob_svc = BlobService(account_name=storage_account_name, account_key=storage_keys.storage_service_keys.primary)
    blob_svc.create_container(container_name)
    logging.info('Creating Container \'{0}\' in Storage account {1} complete'.format(container_name, storage_account_name))


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


def mount_distributed_file_system(name, vm_resources):
    fileshare_storage_account = name
    fileshare_name = 'sharedfs'
    fileshare_keys = create_distributed_file_system(fileshare_storage_account, fileshare_name)

    script_lines = [
        "STORAGE_ACCOUNT_NAME='{}'".format(fileshare_storage_account),
        "STORAGE_ACCOUNT_KEY='{}'".format(fileshare_keys.storage_service_keys.primary),
        "FILESHARE_NAME='{}'".format(fileshare_name),
        "FILESHARE_PATH=\"//${STORAGE_ACCOUNT_NAME}.file.core.windows.net/${FILESHARE_NAME}\"",
        "sudo chown azureuser /opt",
        "mkdir -p /opt/fileshare",
        "sudo mount $FILESHARE_PATH /opt/fileshare -t cifs -o " +
        "\"vers=2.1,dir_mode=0777,file_mode=0777,username=${STORAGE_ACCOUNT_NAME},password=${STORAGE_ACCOUNT_KEY}\""]

    logging.info('Mounting Distributed FileSystem {}'.format(fileshare_name))
    command = ';\n'.join(script_lines)
    logging.debug('Mounting Command below')
    logging.debug(command)
    for vm in vm_resources:
        logging.info('Mounting DFS in VM {}'.format(vm.name))
        stdin, stdout, stderr, ssh = vm.execute_command(command)
        for line in stdout:
            logging.info('MOUNTING_STDOUT:{}'.format(line))
        for line in stderr:
            logging.info('MOUNTING_STDERR:{}'.format(line))
        ssh.close()
    logging.info('Mounting Distributed FileSystem {} complete'.format(fileshare_name))

    return '/opt/fileshare'
