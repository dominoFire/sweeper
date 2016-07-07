import unittest
import logging
from sweeper.scheduler.common import estimate_resources
from sweeper import Workflow
import sweeper.cloud.azure.manager as az_mgr
from sweeper.cloud.azure import AzureCloudProvider
from pprint import PrettyPrinter
import os
import time
import uuid

pp = PrettyPrinter(indent=1)
logging.basicConfig(filename='test_workflow.log', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())


class WorkflowTest(unittest.TestCase):
    def test(self):
        w = Workflow.read_workflow('examples/test/workflow.yaml')
        pp.pprint(w.__dict__)
        self.assertEqual(len(w.tasks), 4)
        self.assertEqual(len(w.dependencies), 4)

    def test_grid(self):
        w = Workflow.read_workflow('examples/gridsearch/workflow.yaml')
        pp.pprint(w.__dict__)


class ResourceEstimatorTest(unittest.TestCase):
    def test(self):
        w = Workflow.read_workflow('examples/test/workflow.yaml')
        r = estimate_resources(w)
        self.assertEqual(r, 2)
        print('Resources', r)
        w = Workflow.read_workflow('examples/multilayer/workflow.yaml')
        r = estimate_resources(w)
        print('Resources', r)
        self.assertEqual(r, 4)
        w = Workflow.read_workflow('examples/weird/workflow.yaml')
        r = estimate_resources(w)
        print('Resources', r)

        w = Workflow.read_workflow('examples/gridsearch/workflow.yaml')
        r = estimate_resources(w)
        print('Resources', r)


def check_azure_env_vars():
    subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID')
    pem_file = os.environ.get('AZURE_PEM_FILE')

    if subscription_id is None or pem_file is None:
        raise ValueError('To run this test, set env-vars: AZURE_SUBSCRIPTION_ID, AZURE_PEM_FILE')

    return subscription_id, pem_file

class PlannerTest(unittest.TestCase):
    def test(self):
        subscription_id, pem_file = check_azure_env_vars()
    
        az = AzureCloudProvider(subscription_id, pem_file)
        for i in range(20):
            configs = az.possible_configs(i)
            logging.debug("Possible configs of {}: {} => {}".format(i, len(configs), configs))
        

class CreateVMTest(unittest.TestCase):
    def test(self):
        subscription_id, pem_file = check_azure_env_vars()
    
        az = AzureCloudProvider(subscription_id, pem_file)

        res_name = 'sweepertest{}'.format(str(uuid.uuid4())[:8])
        #import azure
        #azure.http.httpclient.DEBUG_REQUESTS = True
        #azure.http.httpclient.DEBUG_RESPONSES = True

        res_config = az.get_config('Standard_D4')
        res_config.service_certificate_path = './certs/service_certificate.cer'
        try:
            res = az.create_vm(res_name, res_config)
            ssh = res.create_ssh_client()
            logging.info(res.__dict__)
            _, stdout, _ = ssh.exec_command('ps aux')
            for line in stdout:
                logging.debug(line)
            logging.info('Waiting some time for shutting down')
            time.sleep(40)
            ssh.close()
            az.delete_vm(res_name)
        except Exception as ex:
            logging.error('TEST exeption:, {0}'.format(ex))
            raise ex


class DeleteVMTest(unittest.TestCase):
    def test(self):
        res_name = 'daftgrunge'
        az_mgr.delete_resource(res_name)


if __name__ == '__main__':
    unittest.main()
