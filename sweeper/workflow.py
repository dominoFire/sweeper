__author__ = '@dominofire'

from sweeper import Task
import copy
import logging
import re
import yaml
import sweeper.utils as utils


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
        self.dependencies = dependencies_list
        """List of 2D tuples that indicates that (a, b) mean Task a precedes Task b """

        self._validate_empty()
        self._validate_task_names()

        for dep in self.dependencies:
            # print dep[0]
            dep[0].add_successor(dep[1])
            dep[1].add_parent(dep[0])

        self._validate_cycle()

    def _validate_empty(self):
        if len(self.tasks) == 0:
            raise ValueError('Workflow with no tasks')

        return True

    def _validate_task_names(self):
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

    def _validate_cycle(self):
        visited = set()

        raise ValueError('TODO!!!!!!!!!!')

        for t in self.tasks:
            visited.add(t)
        print(visited)


    @staticmethod
    def expand_nodes():
        # Variable extraction
        pattern_var = r'@([_a-zA-Z]+)'
        grid_vars = re.findall(pattern_var, t.command)
        # variable description checking
        for grid_var in grid_vars:
            if not grid_var in task_desc['param_grid'].keys():
                raise ValueError('Variable {} not found in params_grid'.format(grid_var))
        # expand grid
        params_grid = task_desc['param_grid']
        p_grid = {k: params_grid[k] for k in grid_vars}
        args_list = utils.expand_list(**p_grid)
        # command substitution
        command_template = re.sub(pattern_var, r'{\1}', t.command)
        for i, args in enumerate(args_list):
            task_copy = copy.copy(t)
            task_copy.command = command_template.format(**args)
            task_copy.name = '{}_{}'.format(task_copy.name, i)
            task_copy.grid_params = args
            logging.debug(task_copy.command)
            task_list.append(task_copy)

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
        depependencies_list = []

        # Parsing
        for task_desc in wf_spec['workflow']:
            task_name = task_desc['name']

            task_command = task_desc['command']
            if inject_profiling:
                task_command = '/usr/bin/time -f "%e,%U,%S" -o {}.time {}'.format(task_name, task_command)

            t = Task(task_name, task_command)

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

            if 'param_grid' in task_desc:
                if not isinstance(task_desc['param_grid'], dict):
                    raise ValueError('param_grid field must be a dict')
                t.param_grid = task_desc['param_grid']

            if 'depends' in task_desc:
                if not isinstance(task_desc['depends'], list):
                    raise ValueError('depends field must be a list')
                t.dependency_names = task_desc['depends']

            task_list.append(t)

        # Dependency checking
        for t in task_list:
            for dn in t.dependency_names:
                t_list = [x for x in task_list if x.name == dn]
                if len(t_list) == 0:
                    raise ValueError('Task dependency not found: {}'.format(dn))
                elif len(t_list) > 1:
                    raise ValueError('Task dependency with multiple task matches: {}'.format(dn))
                td = t_list[0]
                depependencies_list.append((td, t))

        wf = Workflow(task_list, depependencies_list)

        return wf
