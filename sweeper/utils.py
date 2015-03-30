import os


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
    while not predicate_func(kwargs):
        pass