from sweeper.cloud.azure.subscription import sms

vm_name = 'sweepervm'

#print 'Deleting VM (deployment)'
sms.delete_deployment(service_name=vm_name, deployment_name=vm_name)
