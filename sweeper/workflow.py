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

        if not self._validate_empty():
            raise ValueError('Workflow must have at least one task')
        if not self._validate_task_names():
            raise ValueError('Workflow tasks must not have tasks with the same names')

        for dep in self.dependencies:
            # print dep[0]
            dep[0].add_successor(dep[1])
            dep[1].add_parent(dep[0])

        if not self._validate_cycle():
            raise ValueError('Workflow tasks must not have cyclic dependencies')

        tasks_expanded = []
        for t in self.tasks:
            if len(t.param_grid) > 0:
                logging.info('Expanding {}'.format(t))
                logging.info('ParamGrid: {}'.format(t.param_grid))
                expanded = self.expand_nodes(t)
                if expanded > 0:
                    tasks_expanded.append(t)
                else:
                    logging.warning(
                        'Task {} with param_grid that doesn\'t expand nodes. '.format(t.name) +
                        'The task will not be deleted')
        logging.debug('Expanded tasks: {}'.format(tasks_expanded))

        for t in tasks_expanded:
            self.remove_task(t)

        if not self._validate_task_names():
            raise ValueError('Workflow tasks must not have tasks with the same names')

        if not self._validate_cycle():
            raise ValueError('Workflow tasks must not have cyclic dependencies')

    def _validate_empty(self):
        """
        Checks if the workflow has tasks
        :return: True if the workflow has at least one task
        """
        if len(self.tasks) == 0:
            raise ValueError('Workflow with no tasks')

        return True

    def _validate_task_names(self):
        """
        Check if there are duplicated names in task names
        :return: True if the workflow has not task with duplicated names
        """
        names_set = set()
        for t in self.tasks:
            if t.name in names_set:
                raise ValueError('Duplicated names not allowed in workflow tasks')
            else:
                names_set.add(t.name)

        return True

    def _validate_cycle(self):
        """
        Checks if the workflow has cyclic dependencies
        :return: True if the workflow has not cyclic dependencies
        """
        visited = set()

        def visit(task_node):
            """
            Visits the node and its successors recursively in order to find a dependency
            """
            visited.add(task_node)
            for succ_task in task_node.successors:
                if succ_task in visited:
                    return False
                else:
                    visit(succ_task)
            visited.remove(task_node)

            return True

        # we have to check cyclic dependencies in every workflow task
        for task in self.tasks:
            if not task in visited:
                valid = visit(task)
                if not valid:
                    return False

        return True

    def expand_nodes(self, t):
        """
        Given a task node t with non-empty param_grid, creates tasks nodes that represent
        parameter sweep combinations.
        NOTE: this method causes side effects
        :type t: task.Task
        :return: The number of expanded nodes
        """
        # Variable extraction
        pattern_var = r'@([_a-zA-Z]+)'
        grid_vars = re.findall(pattern_var, t.command)
        # variable description checking
        for grid_var in grid_vars:
            if not grid_var in t.param_grid.keys():
                raise ValueError('Variable {} not found in params_grid'.format(grid_var))
        # expand grid
        params_grid = t.param_grid
        p_grid = {k: params_grid[k] for k in grid_vars}
        args_list = utils.expand_list(**p_grid)
        # command substitution
        command_template = re.sub(pattern_var, r'{\1}', t.command)
        for i, args in enumerate(args_list):
            task_copy = copy.copy(t)
            task_copy.command = command_template.format(**args)
            task_copy.name = '{}_{}'.format(task_copy.name, i)
            task_copy.grid_params = args
            task_copy.param_grid = {}  # We use this as a flag to expand nodes
            logging.debug(task_copy.command)

            for succ in task_copy.successors:
                succ.parents.append(task_copy)
                succ.dependency_names.append(task_copy.name)
                self.dependencies.append((task_copy, succ))  # Side effect.
            for pred in task_copy.parents:
                pred.successors.append(task_copy)
                self.dependencies.append((pred, task_copy))  # Side effect.

            self.tasks.append(task_copy)

        return len(args_list)

    def remove_task(self, t):
        """
        Remove the task and its dependencies from the workflow
        :param t:
        :return:
        """
        for succ in t.successors:
            succ.parents.remove(t)
            succ.dependency_names.remove(t.name)
        for par in t.parents:
            par.successors.remove(t)

        # As seen on TV
        # http://stackoverflow.com/questions/1207406/remove-items-from-a-list-while-iterating-in-python
        self.dependencies = [d for d in self.dependencies if not(d[0] == t or d[1] == t)]

        self.tasks.remove(t)

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
        dependencies_list = []

        # Parsing
        if not 'workflow' in wf_spec:
            raise ValueError('workflow.yaml file must have "workflow" entry')

        if not 'provider' in wf_spec:
            raise ValueError('workflow.yaml file must have "provider" entry')

        if type(wf_spec['workflow'])!=list:
            raise ValueError('"workflow" entry must be a YAML list')

        if type(wf_spec['provider'])!=dict:
            raise ValueError('"provider" entry must be a YAML dict')


        # A plugin system would be better?
        valid_key = False
        providers = ['localhost', 'azure']
        for k in wf_spec['provider'].keys():
            for v in providers:
                if v == k:
                    valid_key = True
                    break

        if not valid_key:
            raise ValueError('"provider" only support {}'.format(providers))


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
                dependencies_list.append((td, t))

        wf = Workflow(task_list, dependencies_list)

        logging.info('Workflow with {} tasks and {} dependencies'.format(len(wf.tasks), len(wf.dependencies)))

        return wf
