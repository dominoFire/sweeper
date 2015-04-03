from sweeper.cloud.azure import manager as mgr_azure
from sweeper.scheduler import myopic
from sweeper.scheduler.common import estimate_resources, prepare_resrc_config


def run_workflow(workflow):
    # Creamos recursos
    resrc_num = estimate_resources(workflow)

    # Creamos planificacion
    configs = mgr_azure.possible_configs(resrc_num)

    for c in configs:
        sp = myopic.create_schedule_plan(workflow, c)
        print sp

    # Optimizer

    # Creamos recursos
    vm_resources = []
    for idx, config in enumerate(sp.resource_configurations):
        vm = mgr_azure.create_resource(sp.resource_names[idx], config)
        vm_resources.append(vm)

    # Mandamos a ejecutar


    # queuqe based system

    # Destruimos recursos
    for vm in vm_resources:
        mgr_azure.delete_resource(vm.name)

    return sp


def manage_execution(schedule_plan, vm_list):
    pass
