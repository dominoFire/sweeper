__author__ = '@dominofire'

import numpy as np
from cloud.azure import resource_config_factory as cfg_factory
from scheduler.common import get_task_segments


def bin_packing(tasks, resource_configs):
    """
    Given a list of tasks that are locally independent, and a list of ResourceConfig objects,
    finds the mapping between tasks a resource configs that minimizes cost
    :type tasks: list
    :type resource_configs: list
    :return:
    """
    mem_costs = np.zeros((len(tasks), len(resource_configs)))
    visited = np.zeros((len(tasks), len(resource_configs)))
    used = np.zeros(len(resource_configs))
    MAX_VALUE = 100000000.
    mem_costs.fill(MAX_VALUE)

    def all_scheduled():
        """
        Returns a 0 <= x <= 1 value if all task have been mapped
        Otherwise, returns a very large number called MAX_VALUE
        You can think of this function as an predicate to determine if all tasks have been mapped
        with a quality degree of that mapping
        """
        sum_cores = 0.
        sum_sfs = 0.
        for i, n in enumerate(used):
            if n != 0:
                sum_cores += resource_configs[i].cores * n
                sum_sfs += resource_configs[i].speed_factor * n
        if int(sum_cores) != len(tasks):
            return MAX_VALUE
        else:
            # print('Possible solution', sum_cores)
            # for i, n in enumerate(used):
            #     if n != 0:
            #         print(resource_configs[i], 'x', n, '(index {})'.format(i))
            # print()
            return 0. + 1./sum_sfs

    def take(t_i, rc_i):
        """
        Memoized-DP stuff
        """
        if rc_i == len(resource_configs) or t_i == len(tasks):
            return all_scheduled()
        if visited[t_i, rc_i] != 0:
            return mem_costs[t_i, rc_i]

        for y in range(rc_i, len(resource_configs)):
            rc = resource_configs[y]
            t_lim = min(len(tasks), t_i + rc.cores)
            task_complexities = 0.
            taked_cost = 0.
            for tt in tasks[t_i:t_lim]:
                #task_complexities += tt.complexity_factor
                taked_cost = max(taked_cost, tt.complexity_factor / rc.speed_factor * rc.cost_hour_usd * 1000)
            #taked_cost = task_complexities / rc.speed_factor * rc.cost_hour_usd * 1000
            used[y] += 1
            taked = take(t_lim,  0) + taked_cost
            used[y] -= 1
            taked_not = take(t_i, y + 1)
            mem_costs[t_i, y] = min(taked, taked_not)
            if taked < taked_not:
                visited[t_i, y] = 1   # Taked
            else:
                visited[t_i, y] = -1  # Not taked

        return mem_costs[t_i, rc_i]

    resource_mappings = []

    def check_take(t_i, rc_i):
        """
        Checks the 'visited' DP table for build the complete solution (mapping)
        """
        if t_i < len(tasks) and rc_i < len(resource_configs):
            if visited[t_i, rc_i] == 1:
                rc = resource_configs[rc_i]
                t_lim = min(len(tasks), t_i + rc.cores)
                check_take(t_lim, 0)
                resource_mappings.append((tasks[t_i:t_lim], resource_configs[rc_i]))
                #print(rc, 'at task index', t_i, 'cost', mem_costs[t_i, rc_i])
            elif visited[t_i, rc_i] == -1:
                check_take(t_i, rc_i + 1)

    res = take(0, 0)
    #print('Minimum cost: {}'.format(res))
    #print(mem_costs)
    #print('Visited')
    #print(visited)
    #print()
    check_take(0, 0)

    return resource_mappings


def critical_path(workflow):
    """
    Given an sweeper.workflow.Workflow object, calculates the longest sequence of
    dependent tasks
    :param workflow: as sweeper.workflow.Workflow object
    :return: a list with tasks
    """
    selected = {}
    visited = {}

    def visit(task):
        visited[task] = 1
        max_p = 0
        for t_h in task.successors:
            if not t_h in visited:
                v = visit(t_h) + 1
                if v > max_p:
                    max_p = v
                    selected[task] = t_h

        return max_p

    max_w = 0
    top_task = None
    for t in workflow.tasks:
        if not t in visited:
            p = visit(t) + 1
            if p > max_w:
                max_w = p
                top_task = t

    #print('Longest path:', max_w)

    t_k = top_task
    path = []
    while not t_k is None:
        #print(t_k)
        path.append(t_k)
        t_k = selected[t_k] if t_k in selected else None

    return path


def create_schedule_plan_blind(workflow):
    """
    Create a schedule plan using Sweeper's blind algorithm
    (not functional yet)
    :type workflow: workflow.Workflow A workflow object
    :return: a SchedulePlan objet
    """
    segment = get_task_segments(workflow)
    inv_seg = dict()

    for k in segment:
        if not segment[k] in inv_seg:
            inv_seg[segment[k]] = [k]
        else:
            inv_seg[segment[k]].append(k)

    mappings_list = []
    for seg_num in inv_seg:
        print('Segment')
        print(inv_seg[seg_num])
        mappings = bin_packing(inv_seg[seg_num], cfg_factory.list_configs())
        mappings_list.append(mappings)
        print('Mappings')
        print(mappings)
        print()

    path = critical_path(workflow)
    print('Critical path')
    print(path)
