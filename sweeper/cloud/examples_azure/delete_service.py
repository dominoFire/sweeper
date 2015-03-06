from sweeper.cloud.examples_azure.azure_subscription import sms

print 'Delete hosted service'
# Delete hosted service
# NOTE: before you can delete a service, all deployments for the the
# service must first be deleted. (See How to: Delete a deployment for details.)
sms.delete_hosted_service('whitestarvm')
