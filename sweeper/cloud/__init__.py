__author__ = '@dominofire'


def resource_config_combinations(num, resource_configs):
    """
    Computes all the combinations of ResourceConfiguration that have
    exactly 'num' cores
    :param num: Number of required cores
    :param resource_configs: List of ResourceConfig
    :return: a List with all the possible combinations
    """
    combinations = []

    #knackspack via cores
    def resource_combinations(num_req, config_list, res_list, idx):
        if num_req == 0:
            combinations.append(list(config_list))
        else:
            for i in range(idx, len(res_list)):
                cfg = res_list[i]
                if num_req - cfg.cores >= 0:
                    config_list.append(cfg)
                    resource_combinations(num_req - cfg.cores, config_list, res_list, i)
                    config_list.pop()

    resource_combinations(num, [], resource_configs, 0)

    return combinations
