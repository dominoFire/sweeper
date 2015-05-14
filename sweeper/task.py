__author__ = '@dominofire'


class Task:
    """
    Represents a task in the workflow
    """
    def __init__(self, name, cmd):
        self.name = name
        """ A name for the task that is unique among workflow scope """
        self.command = cmd
        """ A valid bash command to be executed """
        # Used in workflow management
        self.parents = []
        """ A list of Tasks that immediately precedes this task in the Workflow """
        # Used in workflow management
        self.successors = []
        """ A list of Tasks that immediately precedes this task in the Workflow """
        self.complexity_factor = 1
        """ A measurement that represents how difficult is this Task. A high value on the complexity factor
        means that it will take more time and resources to completely execute this task"""
        self.param_grid = []
        """ The list of parameters that are been to be probed in this task. NOT FUNCTIONAL YET"""
        self.include_files = []
        """ Paths that points to files required to execute this task """
        self.download_files = []
        """ Paths that downloads files stored in the cloud """

    def add_parent(self, task):
        self.parents.append(task)

    def add_successor(self, task):
        self.successors.append(task)

    def __str__(self):
        return 'Task:{0}'.format(self.name)

    def __eq__(self, other):
        if not isinstance(other, Task):
            return False
        return self.name == other.name

    def __hash__(self):
        return self.name.__hash__()
