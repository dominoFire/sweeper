__author__ = '@dominofire'

import os
import re

from sweeper.resource import ResourceConfig


def get_config(config_name):
    core_var = re.findall(r'localhost_(\d+)', config_name)
    if len(core_var) == 0:
        raise ValueError('No cores number matched in config_name. config_name must be of the form of localhost_num')
    if len(core_var) > 1:
        raise ValueError('Multiple cores number matched')

    c = int(core_var[0])

    rc = ResourceConfig('localhost_{}'.format(c),
                        c,
                        6182,
                        'Localhost',
                        39 * c,
                        c * 2)

    return rc


def list_configs():
    rc_list = []
    for c in range(1, os.cpu_count() - 1):
        rc = get_config('localhost_{}'.format(c))
        rc_list.append(rc)

    return rc_list
