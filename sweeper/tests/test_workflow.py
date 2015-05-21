import unittest
import logging
from sweeper.scheduler.common import estimate_resources
from sweeper import Workflow
import sweeper.cloud.azure.manager as az_mgr
from pprint import PrettyPrinter
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


class PlannerTest(unittest.TestCase):
    def test(self):
        configs = az_mgr.possible_configs(4)
        print('Possible Configs 4: {0}'.format(len(configs)))
        #pp.pprint(configs)
        configs = az_mgr.possible_configs(20)
        print('Possible Configs 20: {0}'.format(len(configs)))
        #pp.pprint(configs)


class CreteVMTest(unittest.TestCase):
    def test(self):
        res_name = 'sweepertest{}'.format(str(uuid.uuid4())[:8])
        #import azure
        #azure.http.httpclient.DEBUG_REQUESTS = True
        #azure.http.httpclient.DEBUG_RESPONSES = True
        try:
            import sweeper.cloud.azure.resource_config_factory as cfg_factory
            res = az_mgr.create_resource(res_name, cfg_factory.get_config('Standard_D1'))
            ssh = res.create_ssh_client()
            logging.info(res.__dict__)
            _, stdout, _ = ssh.exec_command('ps aux')
            for line in stdout:
                logging.debug(line)
            logging.info('Waiting some time for shutting down')
            time.sleep(40)
            ssh.close()
            az_mgr.delete_resource(res_name)
        except Exception as ex:
            logging.error('TEST exeption:, {0}'.format(ex))
            raise ex


class DeleteVMTest(unittest.TestCase):
    def test(self):
        res_name = 'daftgrunge'
        az_mgr.delete_resource(res_name)


if __name__ == '__main__':
    unittest.main()
