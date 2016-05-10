from azure.servicemanagement import *
import os
import sweeper.utils as utils

#Azure subscription ID
subscription_id = '8ea1a328-9162-4a6e-9cdc-fcc8d6766608'
# path to .pem file that includes the certificate to the Azure Account
pem_file = 'mycert.pem'
# path to .cer file
cer_file = 'mycert.cer'
# path to .pfx file
pfx_file = ''  # TODO: How to generate in Linux
# Path to current script directory
path = os.path.realpath(__file__)
curr_path = utils.split_path(path)
# Fullpath for pem_file
pem_base, pem_ext = os.path.splitext(pem_file)
pem_fullpath = utils.join_path(curr_path[0], pem_base, pem_ext)
# Fullpath for cer_file
cer_base, cer_ext = os.path.splitext(cer_file)
cer_fullpath = utils.join_path(curr_path[0], cer_base, cer_ext)
# Fullpath for pfx_fiile
pfx_base, pfx_ext = os.path.splitext(pfx_file)
pfx_fullpath = utils.join_path(curr_path[0], pfx_base, pfx_ext)

#print (pem_fullpath)

# In order to wait for requests, we had to extend the ServiceManagementService class
# But, it's not implemented in all calls
# sms = AzureSMSAsyncHandler(subscription_id, certificate_path)
sms = ServiceManagementService(subscription_id, pem_fullpath)
