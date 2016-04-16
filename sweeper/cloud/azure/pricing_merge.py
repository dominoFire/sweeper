#!/usr/bin/python3

import pandas as pd

if __name__ == '__main__':
    prices = pd.read_csv('azure_pricing_vm_common.csv')
    roles = pd.read_csv('azure_role_sizes.csv')

    role_size = {
        'ExtraSmall': 'A0',
        'Small': 'A1',
        'Medium': 'A2',
        'Large': 'A3',
        'ExtraLarge': 'A4'
    }

    def role_name(x):
        if x in role_size.keys():
            return role_size[x]
        ret = x
        if '_' in x:
            ret = x.split('_')[1]
        return ret

    roles['role_name'] = roles.loc[:, 'name'].apply(role_name)

    def tier_name(x):
        if x in role_size.keys():
            return 'Standard'
        ret = 'Standard'
        if '_' in x:
            ret = x.split('_')[0]
        return ret

    roles['tier_name'] = roles.loc[:, 'name'].apply(tier_name)

    def tier_name_from_description(x):
        if 'Basic' in x:
            return 'Basic'
        return 'Standard'

    prices['tier_name'] = prices.loc[:, 'description'].apply(tier_name_from_description)

    # Only we need a subset, using us-west region
    prices = prices[prices.region == 'us-west']

    print (roles.sort(columns='role_name').head(3))

    print (prices.sort(columns='Instance').head(3))

    merged = pd.merge(prices, roles, left_on=['tier_name', 'Instance'], right_on=['tier_name', 'role_name'])

    print (merged.head(3))

    merged.to_csv('data/azure_role_pricing.csv', encoding='utf-8', index=None)