import unittest
from sweeper.scheduler.runner import execute_workflow
import logging


logging.basicConfig(filename='test_overall.log', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())


class OverallTest(unittest.TestCase):

    def test_simple(self):
        execute_workflow('examples/test.yaml', 'test.csv')

    def test_complex(self):
        execute_workflow('examples/multicore.yaml', 'multicore.csv')

    def test_with_files(self):
        execute_workflow('examples/workflow_with_files.yaml', 'workflow_with_files.csv')

    def test_with_export(self):
        execute_workflow('examples/export/workflow.yaml', 'export.csv')


if __name__ == '__main__':
    unittest.main()
