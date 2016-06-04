__author__ = '@dominofire'

import unittest

from sweeper.cloud.azure import AzureCloudProvider


class AzureTestCase(unittest.TestCase):
    def test_list(self):
        print()
        azure = AzureCloudProvider('8ea1a328-9162-4a6e-9cdc-fcc8d6766608', './certs/azure_client.pem')
        for cfg in azure.list_configs():
            self.assertTrue(cfg.config_name is not None)
            self.assertTrue(cfg.provider == 'azure')
            self.assertTrue(cfg.ram_memory is not None)
            self.assertTrue(cfg.cores is not None)
            self.assertTrue(cfg.speed_factor is not None)

    def test_get_config(self):
        print()
        azure = AzureCloudProvider('8ea1a328-9162-4a6e-9cdc-fcc8d6766608', './certs/azure_client.pem')
        try:
            azure.get_config('NOT-FOUND')
        except ValueError:
            print('Cache el error')

        valid_config = 'A11'
        config = azure.get_config(valid_config)
        self.assertTrue(config.config_name == valid_config)
        self.assertTrue(config.cores == 16)


if __name__ == '__main__':
    unittest.main()
