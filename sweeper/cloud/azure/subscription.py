from azure import *
from azure.servicemanagement import *
import os
import sweeper.utils as utils

#Azure subscription ID
subscription_id = '3581f326-7d5d-47c0-a67c-2895eaee6439'
# path to .pem file that includes the certificate to the Azure Account
pem_file = 'mycert.pem'
# path to .cer file
cer_file = 'mycert.cer'
# Path to current script directory
path = os.path.realpath(__file__)
curr_path = utils.split_path(path)
# Fullpath for pem_file
pem_base, pem_ext = os.path.splitext(pem_file)
pem_fullpath = utils.join_path(curr_path[0], pem_base, pem_ext)
# Fullpath for cer_file
cer_base, cer_ext = os.path.splitext(cer_file)
cer_fullpath = utils.join_path(curr_path[0], cer_base, cer_ext)

#print (pem_fullpath)

# In order to wait for requests, we had to extend the ServiceManagementService class
# But, it's not implemented in all calls
# sms = AzureSMSAsyncHandler(subscription_id, certificate_path)
sms = ServiceManagementService(subscription_id, pem_fullpath)