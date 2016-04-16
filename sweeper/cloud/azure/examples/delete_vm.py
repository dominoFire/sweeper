#!/usr/bin/python3

from sweeper.cloud.azure.subscription import sms

if __name__ == '__main__':
    vm_name = 'sweepervm'

    # print 'Deleting VM (deployment)'
    sms.delete_deployment(service_name=vm_name, deployment_name=vm_name)
