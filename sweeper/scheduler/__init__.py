from paramiko import SSHException
from sweeper.cloud.azure import manager as mgr_azure
from sweeper.scheduler import myopic
from sweeper.scheduler.common import estimate_resources, prepare_resrc_config

import threading
import sweeper.utils as utils
import time
import logging


def create_schedule_plan(workflow):
    resrc_num = estimate_resources(workflow)

    # Creamos planificacion
    configs = mgr_azure.possible_configs(resrc_num)

    logging.info('Makepan, Cost')
    for c in configs:
        sp = myopic.create_schedule_plan(workflow, c)
        logging.info('{},{}'.format(sp.makespan, sp.execution_cost))

    return sp


def run_workflow(workflow):
    # Creamos recursos
    """

    :type workflow: sweeper.workflow.Workflow
    :return:
    """

    sp = create_schedule_plan(workflow)
    # Optimizer
    # TODO: just pick the last one

    # Creamos recursos
    vm_resources = []
    for idx, config in enumerate(sp.resource_configurations):
        vm = mgr_azure.create_resource(sp.resource_names[idx], config)
        vm_resources.append(vm)

    # Mandamos a ejecutar
    manage_execution(sp, vm_resources)

    # Destruimos recursos
    for vm in vm_resources:
        mgr_azure.delete_resource(vm.name)

    return sp


class TaskContainer(threading.Thread):
    """
    A class that stores info for executing a task
    in a cloud resource
    """
    def __init__(self, task, vm, start_time_expected):
        threading.Thread.__init__(self)
        self.task = task
        self.vm = vm
        self.start_time_expected = start_time_expected
        self.status_lock = threading.Lock()
        self._status = -1  # not started

    @property
    def status(self):
        #self.status_lock.acquire()
        st = self._status
        #self.status_lock.release()
        return st

    @status.setter
    def status(self, st):
        self.status_lock.acquire()
        self._status = st
        self.status_lock.release()

    def __repr__(self):
        return 'TaskContainer({},{},{})'.format(self.task.name, self.vm.name, self._status)

    #Override
    def run(self):
        try:
            self.status = 0  # running
            logging.debug('Executing Task {}'.format(self.task))
            p_stdin, p_stdout, p_stderr, client = self.vm.execute_command(self.task.command)
            logging.debug('Executing Task {} complete'.format(self.task))

            out = open('{}_stdout.txt'.format(self.task.name), 'w')
            err = open('{}_stderr.txt'.format(self.task.name), 'w')
            block_size = 4096
            buffer_out = p_stdout.read(block_size)
            buffer_err = p_stderr.read(block_size)
            #non blocking
            while len(buffer_out) > 0 or len(buffer_err) > 0:
                if len(buffer_out) > 0:
                    out.write(buffer_out.decode('utf-8'))  # TODO: it would be nicer if we use resource's encoding
                    buffer_out = p_stdout.read(block_size)
                if len(buffer_err) > 0:
                    err.write(buffer_err.decode('utf-8'))  # TODO: it would be nicer if we use resource's encoding
                    buffer_err = p_stderr.read(block_size)
            out.close()
            err.close()

            logging.debug('Disconnecting to resource {}'.format(self.vm.name))
            client.close()
            logging.debug('Disconnecting to resource {} complete'.format(self.vm.name))

            logging.debug('Task {} executed successfully on resource {}'.format(self.task, self.vm.name))
            self.status = 1  # completed
        except SSHException as ex:
            self.status = 2  # error
            logging.error('Error executing task:{}'.format(ex.message))
        except Exception as ex2:
            self.status = 2  # error
            logging.error('Error executing task:{}'.format(ex2.message))


def manage_execution(schedule_plan, vm_list):
    """

    :param schedule_plan: list of sweeper.scheduler.common.ScheduleMapping
    :param vm_list: list of sweeper.resource.Resource
    :return: None
    """
    queue_ready = []  # list of sweeper.scheduler.common.ScheduleMapping
    queue_running = []  # list of sweeper.scheduler.common.ScheduleMapping
    queue_completed = []  # list of sweeper.scheduler.common.ScheduleMapping
    queue_failed = []
    start_time = 0.
    stop_time = 0.

    # map schedulemapping list elements to vm's
    for sm in schedule_plan.schedule_mapping_list:
        r = list(filter(lambda vm: vm.name == sm.resource_schedule.host_name, vm_list))
        if len(r) == 1:
            queue_ready.append(TaskContainer(sm.task, r[0], sm.start_time))

    start_time = time.time()

    # queue based system
    while queue_ready:
        completed_tasks = [x.task for x in queue_completed]
        mapped_tasks = [x for x in queue_ready if utils.contains_list(x.task.parents, completed_tasks)]
        mapped_tasks = sorted(mapped_tasks, key=lambda x: x.start_time_expected)
        #logging.debug('Ready: {}'.format(queue_ready))
        #logging.debug('Running: {}'.format(queue_running))
        #logging.debug('Completed: {}'.format(queue_completed))
        #logging.debug('Failed: {}'.format(queue_failed))
        for tc in mapped_tasks:
            queue_ready.remove(tc)
            queue_running.append(tc)
            tc.start()
        for tc in queue_running:
            st = tc.status
            if st == 1:  # completed
                queue_running.remove(tc)
                logging.debug('Removed task: \'{}\' from queue_running'.format(tc))
                queue_completed.append(tc)
                logging.debug('Added task: \'{}\' to queue_complete'.format(tc))
            elif st == 2:  # failed
                queue_running.remove(tc)
                logging.debug('Removed task: \'{}\' from queue_running'.format(tc))
                queue_failed.append(tc)
                logging.debug('Added task: \'{}\' to queue_failed'.format(tc))
                logging.error('Error in executing task: ', tc.task)
                import sys
                sys.exit(2)

    stop_time = time.time()

    logging.info('Duration: {}'.format(stop_time - start_time))
