from azure import *
from azure.servicemanagement import *

#Azure subscription ID
subscription_id = '3581f326-7d5d-47c0-a67c-2895eaee6439'
#path to .pem file that includes the certificate to the Azure Account
certificate_path = './mycert.pem'

# In order to wait for requests, we had to extend the ServiceManagementService class
# But, it's not implemented in all calls
# sms = AzureSMSAsyncHandler(subscription_id, certificate_path)
sms = ServiceManagementService(subscription_id, certificate_path)
