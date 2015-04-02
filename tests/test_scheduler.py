import unittest
from sweeper.scheduler import run_workflow
import sweeper.workflow
from pprint import PrettyPrinter


pp = PrettyPrinter(indent=1)


class SchedulerTest(unittest.TestCase):
    def test(self):
        wf = sweeper.workflow.read_workflow('examples/multicore.yaml')

        cfgs = run_workflow(wf)


if __name__ == '__main__':
    unittest.main()
