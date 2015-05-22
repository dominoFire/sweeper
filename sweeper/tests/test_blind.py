from sweeper import Workflow

__author__ = '@dominofire'

import unittest
import random
import sweeper.scheduler.manager as man


class MyTestCase(unittest.TestCase):
    def test_first(self):
        w = Workflow.read_workflow('examples/weird/workflow.yaml')
        man.create_schedule_plan_blind(w)

    def test_random(self):
        w = Workflow.read_workflow('examples/weird/workflow.yaml')
        for t in w.tasks:
            t.complexity_factor = random.random() * 10
        man.create_schedule_plan_blind(w)

    def test_blind(self):
        w = Workflow.read_workflow('examples/gridsearch/workflow.yaml')
        man.create_schedule_plan_blind(w)


if __name__ == '__main__':
    unittest.main()
