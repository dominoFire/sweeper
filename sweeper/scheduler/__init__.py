from sweeper.cloud.azure import manager as mgr_azure
from sweeper.scheduler import myopic
from sweeper.scheduler.common import estimate_resources, prepare_resrc_config
import sweeper.utils as utils


def run_workflow(workflow):
    # Creamos recursos
    resrc_num = estimate_resources(workflow)

    # Creamos planificacion
    configs = mgr_azure.possible_configs(resrc_num)

    for c in configs:
        res_list = prepare_resrc_config(c)
        sml = myopic.create_schedule_plan(workflow, res_list)
        utils.plot_gantt_chart(sml)

        print sml
    # Creamos recursos



    # Mandamos a ejecutar

    return configs