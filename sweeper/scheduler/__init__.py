from paramiko import SSHException
from sweeper.cloud.azure import manager as mgr_azure
from sweeper.scheduler import myopic
from sweeper.scheduler.common import estimate_resources, prepare_resrc_config

import threading
import sweeper.utils as utils
import time
import Queue


def run_workflow(workflow):
    # Creamos recursos
    resrc_num = estimate_resources(workflow)

    # Creamos planificacion
    configs = mgr_azure.possible_configs(resrc_num)

    print 'Makepan, Cost'
    for c in configs:
        sp = myopic.create_schedule_plan(workflow, c)
        print sp.makespan, sp.execution_cost

    # Optimizer

    # Creamos recursos
    # vm_resources = []
    # for idx, config in enumerate(sp.resource_configurations):
    #     vm = mgr_azure.create_resource(sp.resource_names[idx], config)
    #     vm_resources.append(vm)
    #
    # # Mandamos a ejecutar
    # # Destruimos recursos
    # for vm in vm_resources:
    #     mgr_azure.delete_resource(vm.name)

    return sp


class TaskContainer(threading.Thread):
    def __init__(self, task, vm, queue_complete):
        threading.Thread.__init__(self)
        self.task = task
        self.vm = vm
        self.lock_status = threading.Lock()
        self.status = -1  # not started
        self.queue_complete = queue_complete

    #Override
    def run(self):
        try:
            p_stdin, p_stdout, p_stderr = self.vm.run_command(self.task.command)
            out = open('{}_stdout.txt'.format(self.task.name), 'w')
            err = open('{}_stderr.txt'.format(self.task.name), 'w')
            block_size = 4096
            buffer_out = p_stdout.read(block_size)
            buffer_err = p_stderr.read(block_size)
            #non blocking
            while len(buffer_out) > 0 or len(buffer_err) > 0:
                if len(buffer_out) > 0:
                    out.write(buffer_out)
                    buffer_out = p_stdout.read(block_size)
                if len(buffer_err) > 0:
                    err.write(buffer_err)
                    buffer_err = p_stderr.read(block_size)
            out.close()
            err.close()
            self.status = 0
        except SSHException, ex:
            self.status = 1
            print ex.message
            pass
        finally:
            self.queue_complete.put((self.task, self.vm, self.status))


def manage_execution(schedule_plan, vm_list):
    """

    :param schedule_plan: sweeper.scheduler.common.ScheduleMapping
    :param vm_list: sweeper.resource.Resource
    :return: None
    """
    # map schedulemapping list elements to vm's
    vm_mappings = []
    for sm in schedule_plan.schedule_mapping_list:
        r = filter(lambda vm: vm.name == sm.resource_schedule.host_name, vm_list)
        vm_mappings.append((sm, r))

    # queue based system
    queue_ready = vm_mappings
    query_running = []
    queue_completed = Queue.Queue(maxsize=len(vm_mappings))
    start_time = None
    started = False
    while queue_ready:
        for t in schedule_plan.workflow.tasks:
            completed_tasks = [x[0].task for x in queue_completed]
            ready_tasks = utils.contains_list(t.parents, completed_tasks)
            mapped_tasks = [x for x in vm_mappings if x[0].task in ready_tasks]
            #hay que ordenar las tareas
            mapped_tasks = sorted(mapped_tasks, key=lambda tpl: tpl[0].start_time)
            for rt in mapped_tasks:
                container = TaskContainer(rt[0].task, rt[1], queue_completed)
                query_running.append(container)
                container.start()
                if not started:
                    start_time = time.time()

    stop_time = time.time()
