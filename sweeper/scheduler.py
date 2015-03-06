__author__ = '@dominofire'


def estimate_resources(workflow):
    """
    Estimate the number of minimum and maximum number
    of resources needed to run the workflow. It
    assumes that each task run in a single resource

    :param workflow: A Workflow instance
    :return: An integer with the recomended number
    of resources needed to run the workflow

    NOTE: you can always run a workflow with just 1 resources
    and a infinte number of resources

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


