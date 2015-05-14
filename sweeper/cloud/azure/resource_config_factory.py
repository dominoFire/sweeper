import pandas as pd

from sweeper.resource import ResourceConfig


def get_config(config_name):
    """
    Retrieves a specific cloud resource combination
    :param config_name:
    :return:
    """
    # TODO: remove hardcoded paths
    configs = pd.read_csv('/home/fer/ITAM/mcc/sweeper/data/azure_role_pricing_bench.csv')

    row = configs[configs.name == config_name]

    if row.shape[0] == 1:
        rc = ResourceConfig(str(row['name'].iat[0]),
                            int(row['cores'].iat[0]),
                            int(row['memory_in_mb'].iat[0]),
                            'Azure',
                            float(row['specfp_estimate'].iat[0]),
                            float(row['price_hour_usd'].iat[0]))
        return rc

    raise ValueError('Sweeper: Role not found: {0}'.format(config_name))


def list_configs():
    """
    Get al available configurations
    :return:
    """
    configs = pd.read_csv('/home/fer/ITAM/mcc/sweeper/data/azure_role_pricing_bench.csv')
    rc_list = [ResourceConfig(str(row[1]['name']),
                              int(row[1]['cores']),
                              int(row[1]['memory_in_mb']),
                              'Azure',
                              float(row[1]['specfp_estimate']),
                              float(row[1]['price_hour_usd'])) for row in configs.iterrows()]

    return rc_list
