import os
import pandas as pd
from rpy2.robjects.packages import importr
import rpy2.robjects as robjects
import pandas.rpy.common as com
import math
from operator import attrgetter



def split_path(file_location):
    """
    Divide un path de noticias en una tupla de la forma (carpeta, nombre, extension)
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


def contains_list(sublst, lst):
    """
    Check if the elements in sublst are all present in lst:
    :param sublst: a list
    :param lst: a list
    :return: True if the elements in sublst are all present in lst, False otherwise
    """
    for se in sublst:
        if not se in lst:
            return False

    return True


def plot_gantt_chart(schedule_mapping_list, filename=None, title='Scheduling plan'):
    """
    Plot a Gantt chart of the SchedulingMapping List
    :param schedule_mapping_list: SchedulingMapping list to plot
    :return: None, plot is
    """
    df_sched = pd.DataFrame()
    df_sched['labels'] = pd.Series([x.resource_schedule.__repr__() for x in schedule_mapping_list])
    df_sched['starts'] = pd.Series([x.start_time for x in schedule_mapping_list])
    df_sched['ends'] = pd.Series([x.start_time + x.duration for x in schedule_mapping_list])

    unique_res_schedule = sorted(list(set(df_sched['labels'])))
    df_sched['labels_id'] = df_sched['labels'].apply(lambda x: unique_res_schedule.index(x) + 1)
    df_sched['task_name'] = pd.Series([x.task.name for x in schedule_mapping_list])

    i_ini = int(math.floor(df_sched.starts.min()))
    i_fin = int(math.ceil(df_sched.ends.max()) + 1)

    plotrix = importr('plotrix')
    grdevices = importr('grDevices')
    graphics = importr('graphics')
    if filename:
        grdevices.pdf(filename, width=6.53, height=3.71)
    plotrix.gantt_chart(com.convert_to_r_dataframe(df_sched),
                        vgridpos=range(i_ini, i_fin),
                        vgridlab=range(i_ini, i_fin),
                        taskcolors=robjects.r.rainbow(len(schedule_mapping_list)),
                        main=title)
    graphics.text(x=list(df_sched['starts']),
                  y=list(len(unique_res_schedule)+1-df_sched['labels_id']),
                  labels=list(df_sched['task_name']),
                  cex=0.7,
                  pos=4)
    if filename:
        grdevices.dev_off()
