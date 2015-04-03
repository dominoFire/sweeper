import pandas as pd

from sweeper.resource import ResourceConfig


def get_config(config_name):
    configs = pd.read_csv('data/azure_role_pricing.csv')

    row = configs[configs.name == config_name]

    if row and row.shape[0] == 1:
        return ResourceConfig(row['name'], row['cores'], row['memory_in_mb'], 'Azure')

    return None