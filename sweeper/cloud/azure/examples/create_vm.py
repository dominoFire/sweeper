#!/usr/bin/python3

"""
Test drive
Based on
http://azure.microsoft.com/en-us/documentation/articles/cloud-services-python-how-to-use-service-management/#CreateVM
TODO: wait for service created
"""

import time

from azure import *
from azure.servicemanagement import *

from sweeper.cloud.azure.subscription import sms, cer_fullpath

azure.http.httpclient.DEBUG_REQUESTS = True
azure.http.httpclient.DEBUG_RESPONSES = True


def create_network_config(subnet_name=None):
    network = ConfigurationSet()
    network.configuration_set_type = 'NetworkConfiguration'
    network.input_endpoints.input_endpoints.append(
        ConfigurationSetInputEndpoint('SSH', 'tcp', '22', '22'))
    if subnet_name:
        network.subnet_names.append(subnet_name)
    return network


if __name__ == '__main__':
    # just letters and numbers in the name
    vm_name = 'mastershoe'
    vm_location = 'West US'
    # TODO: Automate key & fingerprint generation
    vm_key_fingerprint = '976272116B6DE9398D1032C85B69CD6E6638F691' #mycert.pem

    print('Creating Service')
    service_name = '{0}'.format(vm_name)
    service_label = '{0}'.format(vm_name)
    service_desc = 'Cloud service for VM {0}'.format(vm_name)
    service_location = vm_location
    # You can either set the location or an affinity_group
    req_service = sms.create_hosted_service(service_name, service_label, service_desc, service_location)

    # NOTE: No se pueden hacer waits porque las llamadas a la API TODAVIA NO regresan los callbacks
    # sms.wait_for_operation_status(req_service.request_id)
    time.sleep(10)

    print('Add certificate')
    encoded_cer = ''
    with open(cer_fullpath, 'rb') as cer_file:
        encoded_cer = base64.b64encode(cer_file.read())
    print('------------------- Decoded String -------------------')
    print((base64.b64decode(encoded_cer)))
    print('------------------- Decoded String -------------------')
    # Always put 'pfx' as certificate type
    # No password for '.cer' cetificates
    # See http://stackoverflow.com/questions/18117578/azure-add-certificate-to-cloudservice
    # https://msdn.microsoft.com/en-us/library/azure/ee460817.aspx
    # http://azure.microsoft.com/en-us/documentation/articles/virtual-machines-linux-use-ssh-key/
    result_cert = sms.add_service_certificate(service_name, encoded_cer, 'pfx', '')
    # wait_for_async

    print('Checking certificates')
    cert_result = sms.list_service_certificates(service_name)
    for r in cert_result:
        print(r.__dict__)

    print('Creating LinuxConfigSet')
    # Linux VM configuration, you can use WindowsConfigurationSet
    # for a Windows VM instead
    linux_config = LinuxConfigurationSet(vm_name, 'azureuser', 'Balataraybestos4', True)
    # The paths will be the location in which the service key will be put in
    key_pair = KeyPair(vm_key_fingerprint, '/home/azureuser/id_rsa')
    public_key = PublicKey(vm_key_fingerprint, '/home/azureuser/.ssh/authorized_keys')
    linux_config.ssh.public_keys.public_keys.append(public_key)
    linux_config.ssh.key_pairs.key_pairs.append(key_pair)
    linux_config.disable_ssh_password_authentication = False

    print('Creating Virtual Hard Drive')
    # TODO: Automate configuration of getting VHD image
    # Name of an os image as returned by sms.list_os_images()
    # image_name = 'OpenLogic__OpenLogic-CentOS-62-20120531-en-us-30GB.vhd'
    # image_name = '0b11de9248dd4d87b18621318e037d37__RightImage-CentOS-7.0-x64-v14.2'
    image_name = '0b11de9248dd4d87b18621318e037d37__RightImage-Ubuntu-14.04-x64-v14.2'

    # TODO: Automate configuration of storage account
    # Destination storage account container/blob where the VM disk
    # will be created
    media_link = 'https://sweepervhd.blob.core.windows.net/vmblob/{0}.vhd'.format(vm_name)

    os_hd = OSVirtualHardDisk(image_name, media_link)

    print('Creating Network Configuration (Endpoints)')
    net_cfg = create_network_config()

    print('Creating VM')
    req_vm = sms.create_virtual_machine_deployment(service_name=vm_name,
                                                   deployment_name=vm_name,
                                                   deployment_slot='production',
                                                   label=vm_name,
                                                   role_name=vm_name,
                                                   system_config=linux_config,
                                                   os_virtual_hard_disk=os_hd,
                                                   role_size='Small',
                                                   network_config=net_cfg)

    # NOTE: No se pueden hacer waits porque las llamadas a la API TODAVIA NO regresan los callbacks
    # sms.wait_for_operation_status(req_vm.request_id)
    print(req_vm)

    time.sleep(10)

    # now, how to access the vm

    # print 'Deleting VM (deployment)'
    # sms.delete_deployment(service_name=vm_name, deployment_name=vm_name)

    # print 'Deleting VM (cloud service)'
    # sms.delete_hosted_service(service_name=vm_name)
