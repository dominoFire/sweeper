from azure import *
from azure.servicemanagement import *
from azure_subscription import sms

print 'ServiceMgmtSvc object'
print sms

print 'Available locations'
result = sms.list_locations()
for location in result:
    print 'Location: {0} => {1}'.format(location, location.name)
