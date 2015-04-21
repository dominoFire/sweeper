import unittest
import sweeper
from sweeper.scheduler import create_schedule_plan, run_workflow
import sweeper.utils as utils
import logging


logging.basicConfig(filename='test_overall.log', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())


class OverallTest(unittest.TestCase):
    def test_end2end(self):
        wf = sweeper.workflow.read_workflow('examples/test.yaml')
        sched_plan = run_workflow(wf)
        utils.save_gantt_chart_data(sched_plan.schedule_mapping_list, filename='weird.csv')


if __name__ == '__main__':
    unittest.main()
