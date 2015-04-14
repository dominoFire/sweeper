import unittest
import sweeper.utils as utils
import sweeper.workflow
from pprint import PrettyPrinter
from sweeper.scheduler import run_workflow


pp = PrettyPrinter(indent=1)


class SchedulerTest(unittest.TestCase):
    def test(self):
        wf = sweeper.workflow.read_workflow('examples/weird.yaml')
        sml = run_workflow(wf)
        utils.save_gantt_chart_data(sml.schedule_mapping_list, filename='weird.csv')
        #utils.plot_gantt_chart(sml.schedule_mapping_list, filename='weird.pdf', title='Weird')  # NOT WORK

        wf = sweeper.workflow.read_workflow('examples/multicore.yaml')
        sml = run_workflow(wf)
        utils.save_gantt_chart_data(sml.schedule_mapping_list, filename='multicore.csv')

        wf = sweeper.workflow.read_workflow('examples/multilayer.yaml')
        sml = run_workflow(wf)
        utils.save_gantt_chart_data(sml.schedule_mapping_list, filename='multilayer.csv')


if __name__ == '__main__':
    unittest.main()
