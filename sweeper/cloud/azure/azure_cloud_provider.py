from sweeper.cloud.base import CloudProvider
from azure.servicemanagement import ServiceManagementService
from sweeper.utils import raise_if_none, raise_if_path_not_exists
from sweeper.cloud.azure import list_configs, get_config 


class AzureCloudProvider(CloudProvider):
    """
    Azure Cloud provider for Azure using the classic Service Management API
    """
    def __init__(self, subscription_id, pem_filepath):
        raise_if_none(subscription_id, 'subscription_id')
        raise_if_none(pem_filepath, 'pem_filepath')
        raise_if_path_not_exists(pem_filepath)

        self.name = "Azure"
        """Name of the cloud provider"""
        self.azure_subscription_id = subscription_id
        """Subscription ID in which we can consume Azure resources"""
        self.azure_pem_file = pem_filepath
        """Path to PEM file associated with the Azure subscription"""
        self.sms = ServiceManagementService(subscription_id=self.azure_subscription_id, cert_file=pem_filepath)
        """ServiceManagementService object used to manage al services"""
        self.url = 'https://storage.googleapis.com/sweeper/configs/azure/configs.json'
        """URL to get config data"""

    def delete_vm(self, name):
        pass

    def create_vm(self, name, config, **kwargs):
        pass

    def list_configs(self):
        return list_configs(self.url)

    def get_config(self, config_name):
        return get_config(config_name, self.url)

    @staticmethod
    def create_instance(**kwargs):
        return AzureCloudProvider(kwargs['subscriptionId'], kwargs['pem'])
    