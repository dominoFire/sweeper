__author__ = '@dominofire'

from sweeper.scheduler.manager import run_workflow
from sweeper import Workflow
from sweeper import utils


def execute_workflow(config_file, gantt_csv_path):
    wf = Workflow.read_workflow(config_file)
    utils.export_gml(wf)
    utils.plot_workflow(wf)
    sched_plan = run_workflow(wf)
    utils.save_gantt_chart_data(sched_plan.schedule_mapping_list, filename=gantt_csv_path)


def profile_workflow(config_file, gantt_csv_path):
    wf = Workflow.read_workflow(config_file, inject_profiling=True)
    utils.export_gml(wf)
    utils.plot_workflow(wf)
    sched_plan = run_workflow(wf)
    utils.save_gantt_chart_data(sched_plan.schedule_mapping_list, filename=gantt_csv_path)
