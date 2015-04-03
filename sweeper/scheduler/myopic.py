from common import ScheduleMapping, prepare_resrc_config, SchedulePlan
import sweeper.utils as utils
from operator import attrgetter


def parents_ready_time(parents_list, sched_list):
    """
    Given a list of taks and a list of schedule mappings,
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


def create_schedule_plan(workflow, resrc_config_list):
    """
    Create a schedule plan using the Myopic scheduling algorithm
    :param workflow: A workflow Object
    :param resrc_config_list: a List of Resource Config objects
    :return: a SchedulePlan object
    """
    resrc_schedule_list, resrc_names = prepare_resrc_config(resrc_config_list)
    # all task to be processed
    all_tasks = list(workflow.tasks)
    sched_list = []
    resources = sorted(list(resrc_schedule_list), key=attrgetter('ready_time'))
    while all_tasks:  # While all_tasks is not empty
        sched_tasks = [m.task for m in sched_list]
        ready_tasks = [t for t in all_tasks
                       if (not t in sched_list) and
                       utils.contains_list(t.parents, sched_tasks)]
        for t in ready_tasks:
            r = resources[0]
            d = t.complexity_factor / r.speed_factor
            st = max(r.ready_time, parents_ready_time(t.parents, sched_list))
            sched_list.append(ScheduleMapping(r, t, st, d))
            r.ready_time = st + d
            all_tasks.remove(t)
            resources = sorted(resrc_schedule_list, key=attrgetter('ready_time'))

    return SchedulePlan('myopic', sched_list, workflow, resrc_config_list, resrc_names)
