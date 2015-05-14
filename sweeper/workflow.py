__author__ = '@dominofire'

from sweeper import Task
import yaml


class Workflow:
    """
    Represents a workflow composed by Tasks and its order dependencies.
    """

    def __init__(self, tasks_list, dependencies_list):
        """
        Main constructor
        :rtype : None
        """
        self.tasks = tasks_list
        """List of tasks in the workflow"""
        self._validate_tasks()
        self.dependencies = dependencies_list
        """List of 2D tuples that indicates that (a, b) mean Task a precedes Task b """
        for dep in self.dependencies:
            # print dep[0]
            dep[0].add_successor(dep[1])
            dep[1].add_parent(dep[0])

    def _validate_tasks(self):
        """
        Check if there are duplicated names in task names
        """
        names_set = set()
        for t in self.tasks:
            if t.name in names_set:
                raise ValueError('Duplicated names not allowed in workflow tasks')
            else:
                names_set.add(t.name)
        return True

    @staticmethod
    def read_workflow(filename, inject_profiling=False):
        """
        Read a workflow from a YAML file
        :param filename: Path to YAML file
        :return: a Workflow object
        """
        with open(filename, 'r') as fin:
            wf_spec = yaml.load(fin)
        task_list = []
        dep_list = []

        # Parsing
        for task_desc in wf_spec['workflow']:
            task_name = task_desc['name']
            task_command = task_desc['command']
            if inject_profiling:
                task_command = '/usr/bin/time -f "%e,%U,%S" -o {}.time {}'.format(task_name, task_command)
            t = Task(task_name, task_command)

            if 'param_grid' in task_desc:
                if not isinstance(task_desc['param_grid'], list):
                    raise ValueError('param_grid field must be a list')
                t.param_grid = task_desc['param_grid']
            if 'include_files' in task_desc:
                if not isinstance(task_desc['include_files'], list):
                    raise ValueError('include_files field must be a list')
                t.include_files = task_desc['include_files']
            if 'download_files' in task_desc:
                if not isinstance(task_desc['download_files'], list):
                    raise ValueError('download_files field must be a list')
                t.download_files = task_desc['download_files']

            if inject_profiling:
                t.download_files.append('{}.time'.format(task_name))

            task_list.append(t)

        # Dependency checking
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
