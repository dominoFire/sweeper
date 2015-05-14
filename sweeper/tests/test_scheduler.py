import sweeper.utils as utils
import unittest

from pprint import PrettyPrinter
from scheduler.manager import create_schedule_plan
from sweeper import Workflow

pp = PrettyPrinter(indent=1)


class SchedulerTest(unittest.TestCase):
    def test(self):
        wf = Workflow.read_workflow('examples/weird.yaml')
        sched_plan = create_schedule_plan(wf)
        utils.save_gantt_chart_data(sched_plan.schedule_mapping_list, filename='weird.csv')

        wf = Workflow.read_workflow('examples/multicore.yaml')
        sched_plan = create_schedule_plan(wf)
        utils.save_gantt_chart_data(sched_plan.schedule_mapping_list, filename='multicore.csv')

        wf = Workflow.read_workflow('examples/multilayer.yaml')
        sched_plan = create_schedule_plan(wf)
        utils.save_gantt_chart_data(sched_plan.schedule_mapping_list, filename='multilayer.csv')


if __name__ == '__main__':
    unittest.main()
