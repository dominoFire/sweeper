import unittest
import logging
from sweeper.scheduler.common import estimate_resources
from sweeper.workflow import *
import sweeper.cloud.azure.manager as az_mgr
import sweeper.scheduler as sch
from pprint import PrettyPrinter
import time
import sweeper.utils as utils


pp = PrettyPrinter(indent=1)
logging.basicConfig(filename='test_workflow.log', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())


class WorkflowTest(unittest.TestCase):
    def test(self):
        w = read_workflow('examples/test.yaml')
        pp = PrettyPrinter(indent=1)
        pp.pprint(w.__dict__)
        self.assertEqual(len(w.tasks), 4)
        self.assertEqual(len(w.dependencies), 4)


class ResourceEstimatorTest(unittest.TestCase):
    def test(self):
        w = read_workflow('examples/test.yaml')
        r = estimate_resources(w)
        self.assertEqual(r, 2)
        print('Resources', r)
        w = read_workflow('examples/multilayer.yaml')
        r = estimate_resources(w)
        print('Resources', r)
        self.assertEqual(r, 4)
        w = read_workflow('examples/weird.yaml')
        r = estimate_resources(w)
        print('Resources', r)


class PlannerTest(unittest.TestCase):
    def test(self):
        configs = az_mgr.possible_configs(4)
        print ('Possible Configs 4: {0}'.format(len(configs)))
        #pp.pprint(configs)
        configs = az_mgr.possible_configs(20)
        print ('Possible Configs 20: {0}'.format(len(configs)))
        #pp.pprint(configs)


class CreteVMTest(unittest.TestCase):
    def test(self):
        res_name = 'graphicmodel'
        #import azure
        #azure.http.httpclient.DEBUG_REQUESTS = True
        #azure.http.httpclient.DEBUG_RESPONSES = True
        try:
            import sweeper.cloud.azure.resource_config_factory as cfg_factory
            res = az_mgr.create_resource(res_name, cfg_factory.get_config('Standard_D1'))
            logging.info(res.__dict__)
            utils.wait_for(res.connect_ssh)
            _, stdout, _ = res.execute_command('sleep 60')
            for line in stdout:
                print(line)
            logging.info('Waiting some time for shutting down')
            time.sleep(40)
            az_mgr.delete_resource(res_name)
        except Exception as ex:
            print('Error in test')
            print(ex)
            raise ex


class DeleteVMTest(unittest.TestCase):
    def test(self):
        res_name = 'daftgrunge'
        az_mgr.delete_resource(res_name)


if __name__ == '__main__':
    unittest.main()
