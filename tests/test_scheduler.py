import unittest
from sweeper.scheduler import run_workflow
import sweeper.workflow
import sweeper.utils as utils
from pprint import PrettyPrinter


pp = PrettyPrinter(indent=1)


class SchedulerTest(unittest.TestCase):
    def test(self):
        wf = sweeper.workflow.read_workflow('examples/multicore.yaml')
        sml = run_workflow(wf)
        utils.plot_gantt_chart(sml.schedule_mapping_list, filename='ganttchart.pdf')


if __name__ == '__main__':
    unittest.main()
