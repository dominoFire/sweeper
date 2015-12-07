import unittest
from sweeper.cloud.azure.subscription import sms
from azure.storage.fileshareservice import FileShareService
from sweeper.cloud.azure.manager import wait_for_storage_account, wait_for_request_succeeded
import azure


class TestFileShare(unittest.TestCase):
    def test(self):
        """
        Tests the creation of a file share service
        """
        azure.http.httpclient.DEBUG_REQUESTS = True
        #azure.http.httpclient.DEBUG_RESPONSES = True
        res_name = 'creditgeometry'
        file_share_name = 'myshare'
        storage_account_result = sms.create_storage_account(service_name=res_name,
                                                            description='Storage account for Test {}'.format(res_name),
                                                            label=res_name,
                                                            geo_replication_enabled=None,
                                                            account_type='Standard_LRS',
                                                            location='West US')
        wait_for_request_succeeded(storage_account_result.request_id)
        wait_for_storage_account(res_name)
        storage_keys = sms.get_storage_account_keys(service_name=res_name)
        file_svc = FileShareService(account_name=res_name, account_key=storage_keys.storage_service_keys.primary)
        file_svc.create_file_share(file_share_name, fail_on_exist=True)
        file_svc.delete_file_share(file_share_name, fail_not_exist=True)
        sms.delete_storage_account(res_name)


class TestTables(unittest.TestCase):
    def test(self):
        pass


if __name__ == '__main__':
    unittest.main()
    pass
