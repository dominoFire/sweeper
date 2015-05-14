__author__ = '@dominofire'

from sweeper.scheduler.common import ScheduleMapping, prepare_resrc_config, SchedulePlan
import sweeper.utils as utils
from operator import attrgetter


def parents_ready_time(parents_list, sched_list):
    """
    Given a list of Tasks and a list of schedule mappings,
    finds the earliest start time for a new task preceded by
    task contained in parents_list
    :param parents_list:
    :param sched_list:
    :return:
    """
    max_time = 0

    for sch in sched_list:
        if sch.task in parents_list:
            max_time = max(max_time, sch.start_time + sch.duration)

    return max_time


def create_schedule_plan(workflow, resource_config_list):
    """
    Create a schedule plan using the Myopic scheduling algorithm
    :param workflow: A workflow Object
    :param resource_config_list: a List of Resource Config objects
    :return: a SchedulePlan object
    """
    resource_schedule_list, resource_names = prepare_resrc_config(resource_config_list)
    # all task to be processed
    all_tasks = list(workflow.tasks)
    schedule_mapping_list = []
    resources = sorted(list(resource_schedule_list), key=attrgetter('ready_time'))
    while all_tasks:  # While all_tasks is not empty
        sched_tasks = [m.task for m in schedule_mapping_list]
        ready_tasks = [t for t in all_tasks
                       if (not t in schedule_mapping_list) and
                       utils.contains_list(t.parents, sched_tasks)]
        for t in ready_tasks:
            r = resources[0]
            d = t.complexity_factor / r.speed_factor
            st = max(r.ready_time, parents_ready_time(t.parents, schedule_mapping_list))
            schedule_mapping_list.append(ScheduleMapping(r, t, st, d))
            r.ready_time = st + d
            all_tasks.remove(t)
            resources = sorted(resource_schedule_list, key=attrgetter('ready_time'))

    return SchedulePlan('myopic', schedule_mapping_list, workflow, resource_config_list, resource_names)
