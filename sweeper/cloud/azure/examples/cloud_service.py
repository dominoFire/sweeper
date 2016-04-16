#! /usr/bin/python3

from sweeper.cloud.azure.subscription import sms

if __name__ == '__main__':
    # Create a hosted service
    print('Create hosted service')
    name = 'myhostedservice'
    label = 'myhostedservice'
    desc = 'my hosted service'
    # You can either set the location or an affinity_group
    location = 'West US'
    sms.create_hosted_service(name, label, desc, location)

    print('Query all hosted services')
    # Query for all hosted services
    result = sms.list_hosted_services()
    for hosted_service in result:
        print(hosted_service.__dict__)
        print(hosted_service.hosted_service_properties.__dict__)
        print('Service name: ' + hosted_service.service_name)
        print('Management URL: ' + hosted_service.url)
        print('Affinity group: ' + hosted_service.hosted_service_properties.affinity_group)
        print('Location: ' + hosted_service.hosted_service_properties.location)
        print('')

    print('Get hosted service')
    # Get info for a specific hosted service
    hosted_service = sms.get_hosted_service_properties('myhostedservice')
    print('Service name: ' + hosted_service.service_name)
    print('Management URL: ' + hosted_service.url)
    print('Affinity group: ' + hosted_service.hosted_service_properties.affinity_group)
    print('Location: ' + hosted_service.hosted_service_properties.location)

    print('Delete hosted service')
    # Delete hosted service
    # NOTE: before you can delete a service, all deployments for the the
    # service must first be deleted. (See How to: Delete a deployment for details.)
    sms.delete_hosted_service('myhostedservice')
