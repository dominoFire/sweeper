import unittest
from sweeper.workflow import *
import sweeper.scheduler as sch
from pprint import PrettyPrinter


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


if __name__ == '__main__':
    unittest.main()
