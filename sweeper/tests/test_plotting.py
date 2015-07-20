__author__ = '@dominofire'

import unittest
import sweeper.utils as utils
from sweeper import Workflow
import os


class PlottingText(unittest.TestCase):
    def test_workflow_plot(self):
        wf = Workflow.read_workflow('examples/test/workflow.yaml')
        utils.plot_workflow(wf, file_name='examples/test/workflow.pdf')
        self.assertTrue(os.path.exists('examples/test/workflow.pdf'))

    def test_gml(self):
        wf = Workflow.read_workflow('examples/test/workflow.yaml')
        print(wf.tasks)
        print(wf.dependencies)
        utils.export_gml(wf, file_name='examples/test/workflow.gml')
        self.assertTrue(os.path.exists('examples/test/workflow.gml'))

        wf = Workflow.read_workflow('examples/forests/workflow.yaml')
        print(wf.tasks)
        print(wf.dependencies)
        utils.export_gml(wf, file_name='examples/forests/workflow.gml')
        self.assertTrue(os.path.exists('examples/forests/workflow.gml'))


if __name__ == '__main__':
    unittest.main()
