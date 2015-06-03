__author__ = '@dominofire'

import os

from sweeper.cloud import resource_config_combinations
from sweeper.cloud.localhost import resource_config_factory as config_factory
from sweeper.resource import Resource


def possible_configs(num):
    configs = config_factory.list_configs()
    combs = resource_config_combinations(num, configs)

    return combs


def create_resource(name, config_object):
    res = Resource(config_object, name, 'localhost', None, None)

    return res


def mount_distributed_file_system(name, vm_resources):
    vm_first = vm_resources[0]
    vm_first.execute_command('mkdir ./fileshare')

    return os.path.join(os.getcwd(), 'fileshare')
