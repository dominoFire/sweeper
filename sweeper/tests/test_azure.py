__author__ = '@dominofire'

import unittest

from sweeper.cloud.azure import AzureCloudProvider


class AzureTestCase(unittest.TestCase):
	def test_uno(self):
		azure = AzureCloudProvider('8ea1a328-9162-4a6e-9cdc-fcc8d6766608', './certs/azure_client.pem')
		print(azure.list_configs())

if __name__ == '__main__':
	unittest.main()
