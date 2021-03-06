from functools import reduce
import sys
import sweeper.utils
import uuid

class ResourceSchedule:
    """
    An auxiliary object for creating an managing expected schedules
    Note that scheduling is at core level
    """

    def __init__(self, core_name, host_name, config):
        """
        Base constructor
        :type core_name: str
        :type host_name: str
        :type config: resource.ResourceConfig
        :return:
        """
        self.core_name = core_name
        """ Name that identifies the core inside this machine """
        self.host_name = host_name
        """ A valid host name that identifies the machine """
        self.config = config
        """ A ResourceConfig instance """
        self.ready_time = 0
        """ Indicates the time the machine is ready for executing tasks """
        self.speed_factor = config.speed_factor
        """ SPECfp 2006 score """

    def __repr__(self):
        return '{0}@{1}[{2}]'.format(self.host_name, self.core_name, self.config.config_name)




class ScheduleMapping:
    """
    Represents a mapping between a task and a Resource schedule, including
    scheduling info (start time and duration)
    """
    def __init__(self, res_sched, task, start, duration):
        self.resource_schedule = res_sched
        self.task = task
        self.start_time = start
        self.duration = duration

    @property
    def end_time(self):
        return self.start_time + self.duration

    def __repr__(self):
        return '{0} => {1}, s={2}({3})'.format(self.task, self.resource_schedule, self.start_time, self.duration)


class SchedulePlan:
    """
    Represents a SchedulePlan with all the information needed to execute in cloud Virtual Machines
    """
    def __init__(self, sched_algo, sched_mapping_list, workflow, resource_config_list, resource_names):
        self.scheduling_algorithm = sched_algo
        """ Name of the scheduling algorithm that produces this schedule plan """
        self.schedule_mapping_list = sched_mapping_list
        """ List of ScheduleMapping that contains mappings between Task instances
            and ResourceSchedule instances, with timing info (start_time, duration) """
        self.workflow = workflow
        """ Workflow instance that belongs this schedule plan """
        self.resource_configurations = resource_config_list
        """ The list of sweeper.resource.ResourceConfig objects that represents the resources needed to run the workflow
         mapped in this SchedulePlan object """
        self.resource_names = resource_names
        """ A list of strings that has the names of the resources needed to run the workflow mapped in this SchedulePlan
        object. Note that len(self.resource_configurations) == len(self.resource_names) must be true """

        assert(len(self.resource_configurations) == len(self.resource_names))

    @property
    def execution_cost(self):
        """
        Total expected cost in dollars for executing this workflow in the cloud resources
        :rtype : float
        :return: float
        """
        #TODO: Compute execution cost
        total_cost = 0
        for res_cfg in self.resource_configurations:
            mapped_tasks = list(filter(lambda x: x.resource_schedule.config == res_cfg, self.schedule_mapping_list))
            makespan_res = SchedulePlan._makespan(mapped_tasks)
            total_cost += makespan_res * res_cfg.cost_hour_usd
        return total_cost

    @property
    def makespan(self):
        """
        Total expected execution time of the workflow in this schedule plan
        :return: float
        """
        return SchedulePlan._makespan(self.schedule_mapping_list)

    @staticmethod
    def _makespan(sched_mapping_list):
        """
        Computes makespan from a ScheduleMapping list
        """
        start = reduce(min, [x.start_time for x in sched_mapping_list], 0.)
        end = reduce(max, [x.end_time for x in sched_mapping_list], 0.)
        return end - start

    def lifespans(self):
        ret = []
        for res_name in self.resource_names:
            t_ini = sys.maxsize
            t_end = 0
            # TODO: Optimize this
            for sm in self.schedule_mapping_list:
                if sm.resource_schedule.host_name == res_name:
                    t_ini = min(t_ini, sm.start_time)
                    t_end = max(t_end, sm.start_time, sm.duration)
            ret.append((res_name, t_ini, t_end))
        # First and last tasks

        return ret

def prepare_resrc_config(res_config_list):
    """
    Transform a config list to be used in a scheduling algorithm
    :param res_config_list: a list of ResourceConfig
    :return: a List of ResourceSchedule
    """
    resrc_schedule_list = []

    resource_names = utils.generate_resource_name(len(res_config_list))
    for idx, cfg in enumerate(res_config_list):
        core_list = [ResourceSchedule('Core{0}'.format(i), resource_names[idx], cfg) for i in range(1, cfg.cores+1)]
        resrc_schedule_list = resrc_schedule_list + core_list

    return resrc_schedule_list, resource_names


def get_task_segments(workflow):
    """
    Returns a dict that has the corresponding segment for each task.
    Segments are zero-based numbered
    :param workflow:
    :return:
    """
    visited = dict()
    segment = dict()

    def get_segment(task):
        """
        Calculates recursively the depth of the workflow
        :param task: A task
        :return: Depth of task
        """
        visited[task] = True
        max_seg = 0
        if not task in segment:
            segment[task] = 0
            for p in task.parents:
                v = get_segment(p)
                if v > max_seg:
                    max_seg = v
            segment[task] = max_seg + 1

        return segment[task]

    for t in workflow.tasks:
        get_segment(t)

    return segment


def estimate_resources(workflow):
    """
    Estimate the number of minimum and maximum number
    of resources needed to run the workflow. It
    assumes that each task run in a single resource

    :param workflow: A Workflow instance
    :return: An integer with the recommended number
    of resources needed to run the workflow

    NOTE: you can always run a workflow with just 1 resources
    and a infinite number of resources

    Based on the paper of Saifullah et al.
    http://openscholarship.wustl.edu/cgi/viewcontent.cgi?article=1057&context=cse_research
    """
    segment = get_task_segments(workflow)

    inv_seg = dict()

    for k in segment:
        if not segment[k] in inv_seg:
            inv_seg[segment[k]] = 1
        else:
            inv_seg[segment[k]] += 1

    max_v = 0
    for k in inv_seg:
        max_v = max(inv_seg[k], max_v)

    return max_v
