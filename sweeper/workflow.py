import yaml


class Task:
    def __init__(self, name, cmd):
        self.name = name
        self.command = cmd
        self.parents = []
        self.successors = []
        self.complexity_factor = 1
        self.param_grid = None

    def add_parent(self, task):
        self.parents.append(task)

    def add_successor(self, task):
        self.successors.append(task)

    def __str__(self):
        return 'Task:{0}'.format(self.name)


class Workflow:
    def __init__(self, tasks_list, dependencies_list):
        self.tasks = tasks_list
        self._validate_tasks()
        self.dependencies = dependencies_list
        #TODO: validate dependency no-cycle check
        #TODO: validate dependency with tasks
        for dep in self.dependencies:
            #print dep[0]
            dep[0].add_successor(dep[1])
            dep[1].add_parent(dep[0])

    def _validate_tasks(self):
        names_set = set()
        for t in self.tasks:
            if t.name in names_set:
                raise ValueError('Duplicated names not allowed in workflow tasks')
            else:
                names_set.add(t.name)
        return True


def read_workflow(filename):
    """
    Read a workflow from a YAML file
    :param filename: Path to YAML file
    :return: a Workflow object
    """
    with open(filename, 'r') as fin:
        wf_spec = yaml.load(fin)
    task_list = []
    dep_list = []

    for task_desc in wf_spec['workflow']:
        t = Task(task_desc['name'], task_desc['command'])
        if 'param_grid' in task_desc:
            t.param_grid = task_desc['param_grid']
        task_list.append(t)

    for task_desc in wf_spec['workflow']:
        t = [x for x in task_list if x.name == task_desc['name']][0]
        if 'depends' in task_desc:
            for dep in task_desc['depends']:
                t_parent = [x for x in task_list if x.name == dep]
                if t_parent != [] and len(t_parent) == 1:
                    t_parent = t_parent[0]
                    dep_list.append((t_parent, t))
                else:
                    raise KeyError('Task dependency not found or duplicate task: {0}')

    wf = Workflow(task_list, dep_list)

    return wf
