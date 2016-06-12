import requests
import json

from sweeper.resource import ResourceConfig


def get_config(config_name, url):
    """
    Retrieves a specific cloud resource combination
    :param config_name:
    :return:
    """
    configs = requests.get(url).json()

    row = None
    for r in configs:
        if r['name'] == config_name:
            row = r
            break

    if row is None:
        raise ValueError('config {} not found'.format(config_name))

    rc = ResourceConfig(str(row['name']),
                        int(row['cores']),
                        int(row['memory_in_mb']),
                        row['provider'],
                        float(row['spec_estimate']),
                        float(row['cost_hour_usd']))

    return rc


def list_configs(url):
    """
    Get al available configurations
    :return:
    """
    configs = requests.get(url).json()
    rc_list = [ResourceConfig(str(row['name']),
                              int(row['cores']),
                              int(row['memory_in_mb']),
                              row['provider'],
                              float(row['spec_estimate']),
                              float(row['cost_hour_usd'])) for row in configs]

    return rc_list
