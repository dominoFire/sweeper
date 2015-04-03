class ResourceSchedule:
    """
    An auxilary object for creating an managing expected schedules
    Note that scheduling is at core level
    """
    def __init__(self, core_name, host_name, config):
        self.core_name = core_name
        self.host_hame = host_name
        self.config = config
        self.ready_time = 0
        self.speed_factor = 1

    def __repr__(self):
        return '{0}@{1}[{2}]'.format(self.host_hame, self.core_name, self.config.config_name)


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
    Represents a SchedulePlan with all the information needed to execute in
    cloud Virtual Machines
    """
    def __init__(self, sched_algo, sched_mapping_list, workflow, resource_config_list, resource_names):
        self.scheduling_algorithm = sched_algo
        self.schedule_mapping_list = sched_mapping_list
        self.workflow = workflow
        self.resource_configurations = resource_config_list
        self.resource_names = resource_names

    @property
    def execution_cost(self):
        """
        Total expected cost in dollars for executing this workflow in the cloud resources
        :return: float
        """
        return 0.0

    @property
    def makespan(self):
        """
        Total expected execution time of the workflow in this shecule plan
        :return: float
        """
        start = reduce(min, [x.start_time for x in self.schedule_mapping_list])
        end = reduce(max, [x.end_time for x in self.schedule_mapping_list])
        return end - start


def prepare_resrc_config(res_config_list):
    """
    Transform a config list to be used in a scheduling algorithm
    :param res_config_list: a list of ResourceConfig
    :return: a List of ResourceSchedule
    """
    resrc_schedule_list = []
    resource_names = ['r{0}'.format(idx) for idx, _ in enumerate(res_config_list)]
    for idx, cfg in enumerate(res_config_list):
        core_list = [ResourceSchedule('Core{0}'.format(i), resource_names[idx], cfg) for i in range(1, cfg.cores+1)]
        resrc_schedule_list = resrc_schedule_list + core_list

    return resrc_schedule_list, resource_names


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

    inv_seg = dict()

    for k in segment:
        if not segment[k] in inv_seg:
            inv_seg[segment[k]] = 1
        else:
            inv_seg[segment[k]] += 1

    max_v = 0
    for k, v in inv_seg.iteritems():
        max_v = max(v, max_v)

    return max_v
