import math
import os
import pandas as pd
import rpy2.robjects as robjects

from rpy2.robjects.packages import importr


def split_path(file_location):
    """
    Divide un path de un archivo en una tupla de la forma (carpeta, nombre, extension)
    """
    file_path, file_name = os.path.split(file_location)
    file_base, file_ext = os.path.splitext(file_name)
    return file_path, file_base, file_ext


def join_path(tuple_path):
    """
    Crea una ruta valida desde una tupla de la forma (carpeta, nombre, extension)
    """
    return os.path.join(tuple_path[1], tuple_path[1] + tuple_path[2])


def join_path(base, name, ext):
    """
    Crea una ruta valida desde los parametros base/name.ext
    """
    return os.path.join(base, name + ext)


def wait_for(predicate_func, **kwargs):
    """
    Maintains the current execution thread until the predicate_func(**kwargs) evaluates to True
    :param predicate_func: a Function to evaluate
    :param kwargs: Parameters passed to predicate_func
    :return: None
    """
    if len(kwargs) == 0:
        while not predicate_func():
            pass
    else:
        while not predicate_func(**kwargs):
            pass


def contains_list(sublist, lst):
    """
    Check if the elements in sublst are all present in lst:
    :param sublist: a list
    :param lst: a list
    :return: True if the elements in sublst are all present in lst, False otherwise
    """
    for se in sublist:
        if not se in lst:
            return False

    return True


def filter_any(predicate_func, apply_list):
    return len(list(filter(predicate_func, apply_list))) > 0


def get_gantt_chart_data(schedule_mapping_list):
    dict_sched = {
        'labels': [x.resource_schedule.__repr__() for x in schedule_mapping_list],
        'starts': [x.start_time for x in schedule_mapping_list],
        'ends': [x.start_time + x.duration for x in schedule_mapping_list],
        'task_name': [x.task.name for x in schedule_mapping_list],
        'priorities': [1] * len(schedule_mapping_list)
    }
    unique_labels = sorted(list(set(dict_sched['labels'])))
    dict_sched['labels_id'] = list(map(lambda elem: unique_labels.index(elem)+1, dict_sched['labels']))
    dict_sched['y_coord'] = [len(unique_labels)-x+1 for x in dict_sched['labels_id']]

    return dict_sched


def save_gantt_chart_data(schedule_mapping_list, filename=None):
    """

    :param schedule_mapping_list:
    :param filename:
    """
    dict_sched = get_gantt_chart_data(schedule_mapping_list)
    df_sched = pd.DataFrame(dict_sched)
    df_sched.to_csv(filename, index=None, encoding='utf-8')


def plot_gantt_chart(schedule_mapping_list, filename=None, title='Scheduling plan'):
    """
    Plot a Gantt chart of the SchedulingMapping List
    :param schedule_mapping_list: SchedulingMapping list of SchedulingMapping
    :return: None, plot is
    """
    dict_sched = get_gantt_chart_data(schedule_mapping_list)
    list_sched = robjects.ListVector(dict_sched)

    i_ini = int(math.floor(reduce(min, dict_sched['starts'], 0)))
    i_fin = int(math.ceil(reduce(max, dict_sched['ends'], 0)))
    pseq = range(i_ini, i_fin)

    plotrix = importr('plotrix')
    grdevices = importr('grDevices')
    graphics = importr('graphics')
    if filename:
        grdevices.pdf(filename, width=6.53, height=3.71)
    plotrix.gantt_chart(x=list_sched,
                        vgridpos=pseq,
                        vgridlab=pseq,
                        taskcolors=robjects.r.rainbow(len(schedule_mapping_list)),
                        main=title)
    graphics.text(x=dict_sched['starts'],
                  y=dict_sched['y_coord'],
                  labels=dict_sched['task_name'],
                  cex=0.7,
                  pos=4)
    if filename:
        grdevices.dev_off()
