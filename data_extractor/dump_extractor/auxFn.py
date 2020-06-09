from baseClass import Container


def aux_discrete(distance_list, bin):
    """处理一个距离列表
    
    Args:
        distance_list ([list]): 一个距离列表
        bin ([number]): 宽度
    
    Returns:
        dict: 返回一个离散字典
    """    
    discrete_dict = dict()
    if distance_list:
        max_bin = (max(distance_list)//bin)*bin
    else:
        return discrete_dict
        
    i = 0
    # init
    while i * bin <= max_bin:

        discrete_dict[i*bin] = 0
        i += 1
    for i in distance_list:

        discrete_dict[(i//bin)*bin] += 1

    return discrete_dict


def aux_pbc_validate(distance, boundary_length):
    distance = abs(distance)
    if distance > boundary_length/2:
        distance -= boundary_length
    return distance

def aux_replicate(container):
    import copy
    return copy.deepcopy(container)

def aux_ave_dist(dicts):
    from collections import defaultdict
    temp = defaultdict(float)
    for i in dicts:
        for k,v in i.items():
            temp[k] += v

    return temp

# def aux_ave_time(func, snaps):
#     ans = map(lambda x :func(x), snaps)

#     result_length = len(ans[0])

#     if result_length == 1:
#         temp = 0
#         for i in ans:
#             temp+=i

#         return temp/result_length

#     elif result_length > 1:





def aux_repeat(func, container, **kwargs):

    # validation
    # TODO: 再重写Container类之后换成issubclass（）
    if not isinstance(container, Container):
        raise TypeError('应该传入一个Container以迭代')
    result = list()
    for i in container:
        result.append(func(i, **kwargs))

    return result


