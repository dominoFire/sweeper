import unittest
from sweeper.workflow import *
from sweeper.cloud.azure.manager import possible_configs
import sweeper.scheduler as sch
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=1)

class WorkflowTest(unittest.TestCase):
    def test(self):
        w = read_workflow('../examples/test.yaml')
        pp = PrettyPrinter(indent=1)
        pp.pprint(w.__dict__)
        self.assertEqual(len(w.tasks), 4)
        self.assertEqual(len(w.dependencies), 4)


class ResourceEstimatorTest(unittest.TestCase):
    def test(self):
        w = read_workflow('../examples/test.yaml')
        r = sch.estimate_resources(w)
        self.assertEqual(r, 2)
        print 'Resources', r
        w = read_workflow('../examples/multilayer.yaml')
        r = sch.estimate_resources(w)
        print 'Resources', r
        self.assertEqual(r, 4)


class PlannerTest(unittest.TestCase):
    def test(self):
        configs = possible_configs(4)
        print ('Possible Configs 4: {0}'.format(len(configs)))
        pp.pprint(configs)
        configs = possible_configs(20)
        print ('Possible Configs 20: {0}'.format(len(configs)))
        pp.pprint(configs)

if __name__ == '__main__':
    unittest.main()
