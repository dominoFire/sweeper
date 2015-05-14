__author__ = '@dominofire'

import logging
import sweeper.utils as utils
import sys
import time
import uuid
from sweeper.scheduler.planners import myopic
from sweeper.cloud.azure import manager as mgr_azure
from sweeper.scheduler.task_container import TaskContainer
from sweeper.scheduler.common import estimate_resources


def create_schedule_plan(workflow):
    """
    Evaluates the passed workflow
    :type workflow: workflow.Workflow
    :return:
    """
    resrc_num = estimate_resources(workflow)

    # Creamos planificacion
    configs = mgr_azure.possible_configs(resrc_num)

    logging.info('Makepan, Cost')
    min_cost = sys.float_info.max
    sched_plan = None
    for c in configs:
        sp = myopic.create_schedule_plan(workflow, c)
        cost = sp.execution_cost
        if cost < min_cost:
            sched_plan = sp
        logging.info('{},{}'.format(sp.makespan, sp.execution_cost))

    return sched_plan


def run_workflow(workflow):
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

    # Fieshare
    fileshare_storage_account = 'sweeperdfs{1}'.format(idx, str(uuid.uuid4())[0:8])
    fileshare_name = 'sharedfs'
    fileshare_keys = mgr_azure.create_distributed_file_system(fileshare_storage_account, fileshare_name)

    # TODO: Refactor in a method
    script_lines = [
        "STORAGE_ACCOUNT_NAME='{}'".format(fileshare_storage_account),
        "STORAGE_ACCOUNT_KEY='{}'".format(fileshare_keys.storage_service_keys.primary),
        "FILESHARE_NAME='{}'".format(fileshare_name),
        "FILESHARE_PATH=\"//${STORAGE_ACCOUNT_NAME}.file.core.windows.net/${FILESHARE_NAME}\"",
        "sudo chown azureuser /opt",
        "mkdir -p /opt/fileshare",
        "sudo mount $FILESHARE_PATH /opt/fileshare -t cifs -o " +
        "\"vers=2.1,dir_mode=0777,file_mode=0777,username=${STORAGE_ACCOUNT_NAME},password=${STORAGE_ACCOUNT_KEY}\""]

    logging.info('Mounting Distributed FileSystem {}'.format(fileshare_name))
    command = ';\n'.join(script_lines)
    logging.debug('Mounting Command below')
    logging.debug(command)
    for vm in vm_resources:
        stdin, stdout, stderr, ssh = vm.execute_command(command)
        for line in stdout:
            logging.info('MOUNTING_STDOUT:{}'.format(line))
        for line in stderr:
            logging.info('MOUNTING_STDERR:{}'.format(line))
    ssh.close()
    logging.info('Mounting Distributed FileSystem {} complete'.format(fileshare_name))

    # TODO: Upload files
    vm_first = vm_resources[0]
    logging.info('Uploading files to Distributed FileSystem {} using VM {}'.format(fileshare_storage_account, vm_first.name))
    for task in workflow.tasks:
        for fp in task.include_files:
            folder, basename, ext = utils.split_path(fp)
            vm_first.put_file(fp, utils.join_path('/opt/fileshare', basename, ext))
    logging.info('Uploading files to Distributed FileSystem {} using VM {} complete'.format(fileshare_storage_account, vm_first.name))

    # Mandamos a ejecutar
    manage_execution(sp, vm_resources)

    # Destruimos recursos
    for vm in vm_resources:
        mgr_azure.delete_resource(vm.name)

    return sp


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
    while len(queue_ready) > 0 or len(queue_running) > 0:
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
