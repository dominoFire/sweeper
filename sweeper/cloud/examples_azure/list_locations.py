from sweeper.cloud.examples_azure.azure_subscription import sms

print 'ServiceMgmtSvc object'
print sms

print 'Available locations'
result = sms.list_locations()
for location in result:
    print 'Location: {0} => {1}'.format(location, location.name)
