from tqdm import tqdm

from aux_func import *
from baseClass import *
from containerClass import *
from groupClass import *

import numpy as np


def com_gyration(mol, xi=3, yi=4, zi=5):
    """
    计算均方回转半径

    Args:
        mol (Molecule instance): 传入单链，一个Molecule实例
        xi (int, optional): 未折叠的x在dump文件中的位置. Defaults to 3.
        yi (int, optional): 未折叠的y在dump文件中的位置. Defaults to 4.
        zi (int, optional): 未折叠的z在dump文件中的位置. Defaults to 5.

    Returns:
        [float]: 均方末端距。$\overline{S^2}$
    """
    xa = ya = za = 0
    gy2 = 0
    n = len(mol)

    # compute mass center
    for i in mol:

        xa += i[xi]
        ya += i[yi]
        za += i[zi]

    xa = xa/n
    ya = ya/n
    za = za/n

    print(f'mass center: ({xa}, {ya}, {za})')

    for i in mol:

        gy2 += (i[xi] - xa)**2 + (i[yi] - ya)**2 + (i[zi] - za)**2
    gy2 /= n
    print(f'mean square gyration radius: {gy2}')
    return gy2


def com_e2ed(mol, xi=3, yi=4, zi=5):
    """
    计算均方末端据

    Args:
        mol (Molecule): Molecule类
        xi (int, optional): 同上. Defaults to 3.
        yi (int, optional): 同上. Defaults to 4.
        zi (int, optional): 同上. Defaults to 5.

    Returns:
        float: $\overline{h^2}$
    """
    return (mol[0][xi] - mol[-1][xi])**2 + (mol[0][yi] - mol[-1][yi])**2 + (mol[0][zi] - mol[-1][zi])**2


def com_rdf(center, pair, bin, cutoff, xp=3, yp=4, zp=5, mol_id=1):  # ignore cutoff first
    """径向分布函数 g(r)是距离一个原子为 r 时找到另一个原子的概率 ,g (r)是一个量纲为 1的量。

    Returns:
        [type]: [description]
    """

    boundary_x = center.boundary_x
    boundary_y = center.boundary_y
    boundary_z = center.boundary_z

    c = center.length
    p = pair.length

    global_rho = p / (boundary_x * boundary_y * boundary_z)

    all_distance_lists = list()  # 储存了所有距离信息

    all_discrete_dicts = list()  # 储存了所有离散信息

    for i in tqdm(center, '开始计算径向分布函数', c):

        xi, yi, zi, mol_id_i = i[xp], i[yp], i[zp], i[mol_id]

        distance_list = list()  # 直接储存了所有对距离

        # 仅对一个粒子和目标群体生效，在第二个粒子时被重置

        for j in pair:

            xj, yj, zj, mol_id_j = j[xp], j[yp], j[zp], j[mol_id]

            if mol_id_i == mol_id_j:
                continue

            dx = xj - xi
            dy = yj - yi
            dz = zj - zi

            dx = aux_pbc_validate(dx, boundary_x)
            dy = aux_pbc_validate(dy, boundary_y)
            dz = aux_pbc_validate(dz, boundary_z)

            dis = (dx**2 + dy**2 + dz**2)**0.5

            if dis > cutoff:
                continue

            distance_list.append(dis)

        discrete_dict = aux_discrete(distance_list, bin)

        all_distance_lists.append(distance_list)
        all_discrete_dicts.append(discrete_dict)

    # average

    temp = aux_ave_dist(all_discrete_dicts)

    for k, v in temp.items():
        if v == 0:
            continue
        r = k
        dr = bin
        volumn = 4*3.14159*r**2*dr

        temp[k] = temp[k] / c / volumn / global_rho


    return temp


def com_rdf_axis(part, bin):
    """计算接枝链上单元离轴心的距离

    Args:
        part (Part容器): 传入容器，第一个是轴的分子，剩下的是接枝链分子

    Returns:
        x：距离；y平均距离
    """

    boundary_x = part[0].boundary_x
    boundary_y = part[0].boundary_y
    boundary_z = part[0].boundary_z

    rod = part[0]

    # 直线向量
    # [3:]是硬编码的坐标，一行原子后三位
    rod_head = np.array(rod[0][3:])
    rod_end = np.array(rod[-1][3:])
    rod_vector = rod_end - rod_head

    all_discrete_dicts = list()

    # 接枝链长度
    grafted_number = len(part[1:])

    grafted_length = len(part[1:][0])

    grafted_atom_number = grafted_length * grafted_number

    global_rho = grafted_atom_number / (boundary_x * boundary_y * boundary_z)

    # 算graft上每个珠子到棒的距离
    for i in part[1:]:  # i -> molecule
        diss = list()
        for j in i:  # j -> atom

            graft_end = np.array(j[3:])
            graft_vector = graft_end - rod_head
            dis = np.linalg.norm(
                np.cross(rod_vector, graft_vector)) / np.linalg.norm(rod_vector)

            if dis > grafted_length:
                j[3] -= boundary_x
                j[4] -= boundary_y
                j[5] -= boundary_z
                graft_end = np.array(j[3:])
                graft_vector = graft_end - rod_head
                dis = np.linalg.norm(np.cross(rod_vector, graft_vector)) / np.linalg.norm(rod_vector)


            diss.append(dis)
        all_discrete_dicts.append(aux_discrete(diss, bin))

    # 结果平均

    temp = aux_ave_dist(all_discrete_dicts)

    rod_length = (len(rod) - 1)*1

    for k, v in temp.items():
        if v == 0:
            continue
        r = k
        dr = bin
        volumn = 3.14159*bin*(2*r+bin)*rod_length

        temp[k] = temp[k] / grafted_number / global_rho / volumn


    return temp





def com_bond_orientation(part):
    """计算接枝链取向
    """
    rod = part[0]

    # 直线向量
    # [3:]是硬编码的坐标，一行原子后三位
    rod_head = np.array(rod[0][3:])
    rod_end = np.array(rod[-1][3:])
    rod_vector = rod_end - rod_head

    # 算graft上每个珠子到棒的距离
    vectors = list()
    for i in part[1:]:  # i -> molecule
        beads = list()
        for j in i:  # j -> atom
            b = np.array(j[3:])
            beads.append(b)

            if len(beads) == 3:
                del beads[0]
            elif len(beads) == 2:
                graft_vector = beads[1] - beads[0]
                cos = np.dot(rod_vector, graft_vector) / \
                    (np.linalg.norm(rod_vector) * np.linalg.norm(graft_vector))

                vectors.append(cos**2)

    def p(cos):
        return 0.5*(3*cos**2-1)

    vectors_ave = p(sum(vectors)/len(vectors))
    vectors_uplim = p(max(vectors))
    vectors_lolim = p(min(vectors))

    return (vectors_ave, vectors_uplim, vectors_lolim)
