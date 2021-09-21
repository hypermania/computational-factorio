import random
import copy
import numpy as np
import time

#import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches


# Constraint Graphs

# Constructs the horizontal and vertical constraint graph from sequence pair
def constraint_graph(gamma_plus, gamma_minus):
    constraints_plus = set()
    constraints_minus = set()
    for i in range(module_num):
        for j in range(i+1, module_num):
            constraints_plus.add((gamma_plus[i], gamma_plus[j]))
            constraints_minus.add((gamma_minus[i], gamma_minus[j]))

    G_H = {}
    G_V = {}
    for node in range(module_num):
        G_H[node] = ['s']
        G_V[node] = ['s']
    G_H['t'] = list(range(module_num))
    G_V['t'] = list(range(module_num))
        
    for pair in constraints_minus:
        if pair in constraints_plus:
            G_H[pair[1]].append(pair[0])
        else:
            G_V[pair[1]].append(pair[0])
            
    return (G_H, G_V)

# Returns a dict that contains the longest path of each node from s
def longest_path_from_s(G, weight:dict):
    result = {}
    def compute_result(node:int):
        if node in result:
            return result[node]
        
        if node == 's':
            result[node] = 0
            return result[node]
        
        max_length = 0
        for pred in G[node]:
            max_length = max(max_length, compute_result(pred) + weight[pred])
        result[node] = max_length
        return result[node]
        
    #for node in range(len(weight) - 2):
    #    compute_result(node)
    compute_result('t')
    
    return result

def draw_packing(d_h, d_v, module_width, module_height):
    module_num = len(module_width) - 2
    fig, ax = plt.subplots()
    for node in range(module_num):
        verts = [
            (d_h[node], d_v[node]),  # left, bottom
            (d_h[node], d_v[node] + module_height[node]),  # left, top
            (d_h[node] + module_width[node], d_v[node] + module_height[node]),  # right, top
            (d_h[node] + module_width[node], d_v[node]),  # right, bottom
            (d_h[node], d_v[node]),  # ignored
        ]
    
        codes = [
            Path.MOVETO,
            Path.LINETO,
            Path.LINETO,
            Path.LINETO,
            Path.CLOSEPOLY,
        ]

        path = Path(verts, codes)
        patch = patches.PathPatch(path, facecolor='gray', lw=2)
        ax.add_patch(patch)
        ax.text(*(d_h[node] + module_width[node]/2, d_v[node] + module_height[node]/2), node)

    bound = max(max(d_h.values()), max(d_v.values()))
    ax.set_xlim(-1, bound+1)
    ax.set_ylim(-1, bound+1)
    plt.show()

"""
def compute_init_temp(curr_pair, module_width_dict, module_height_dict):
    curr_cost = area(curr_pair, module_width_dict, module_height_dict)
    module_num = len(curr_pair[0])

    n = 0
    sum_cost = 0
    sum_cost_sqr = 0
    for select_seq in range(0, 2):
        for idx_old in range(0, module_num-1):
            for idx_new in range(0, module_num-1):
                if idx_old == idx_new:
                    continue
                gamma_new = curr_pair[select_seq]
                temp = gamma_new[idx_old]
                gamma_new.remove(temp)
                gamma_new.insert(idx_new, temp)
                trial_pair = (curr_pair[0] if select_seq==1 else gamma_new,
                              curr_pair[1] if select_seq==0 else gamma_new)
                trial_cost = area(trial_pair, module_width_dict, module_height_dict)
                delta_cost = trial_cost - curr_cost

                n += 1
                sum_cost += delta_cost
                sum_cost_sqr += delta_cost ** 2

    avg_cost = sum_cost / n
    std_cost = np.sqrt(sum_cost_sqr / n - avg_cost ** 2)

    return 10 * (avg_cost + 3 * std_cost)
"""
"""
def area(pair, module_width_dict, module_height_dict):
    G_H, G_V = constraint_graph(*pair)

    d_h = longest_path_from_s(G_H, module_width_dict)
    d_v = longest_path_from_s(G_V, module_height_dict)

    #return max(d_h['t'] / d_v['t'], d_v['t'] / d_h['t']) ** 0.25 * (d_h['t'] * d_v['t']) ** 0.5
    return (d_h['t'] * d_v['t']) ** 0.5 
"""

def cost(soln):
    G_H, G_V = constraint_graph(*(soln[0:2]))

    d_h = longest_path_from_s(G_H, soln[2])
    d_v = longest_path_from_s(G_V, soln[3])

    #return max(d_h['t'] / d_v['t'], d_v['t'] / d_h['t']) ** 0.25 * (d_h['t'] * d_v['t']) ** 0.5
    #return (d_h['t'] * d_v['t']) ** 0.5
    return max(d_h['t'], d_v['t'])



# Initialize Problem
module_num = 200

module_width_dict = {node: random.randint(10,50) for node in range(module_num)}
module_width_dict['s'] = 0
module_width_dict['t'] = 0
module_height_dict = {node: random.randint(5,15) for node in range(module_num)}
module_height_dict['s'] = 0
module_height_dict['t'] = 0

# Initialize Solution
gamma_plus = list(np.random.permutation(module_num))
gamma_minus = list(np.random.permutation(module_num))

curr_soln = (gamma_plus, gamma_minus, module_width_dict, module_height_dict)
curr_cost = cost(curr_soln)

min_soln = curr_soln
min_cost = curr_cost

#T_0 = compute_init_temp(curr_pair, module_width_dict, module_height_dict)

"""
import cProfile, pstats, io
from pstats import SortKey
pr = cProfile.Profile()
pr.enable()
"""


t_start = time.time()

i = 0
T_init = 50.0
T_end = 0.2
steps = 1e6
T_ratio = np.exp(np.log(T_init / T_end) / steps)
T = T_init
while T > T_end:
    i += 1

    # Select kind of mutation
    mutate_choice = random.randint(0, 2)

    if mutate_choice == 0: # Exchange two modules in the first sequence
        idx_1, idx_2 = random.sample(range(module_num), k=2)
        gamma_new = curr_soln[0].copy()
        temp = gamma_new[idx_1]
        gamma_new[idx_1] = gamma_new[idx_2]
        gamma_new[idx_2] = temp
        trial_soln = (gamma_new, curr_soln[1], curr_soln[2], curr_soln[3])
    elif mutate_choice == 1: # Exchange two modules names both in the first sequence and the second sequence
        idx_1, idx_2 = random.sample(range(module_num), k=2)
        gamma_new_1, gamma_new_2 = curr_soln[0].copy(), curr_soln[1].copy()
        temp = gamma_new_1[idx_1]
        gamma_new_1[idx_1] = gamma_new_1[idx_2]
        gamma_new_1[idx_2] = temp
        temp = gamma_new_2[idx_1]
        gamma_new_2[idx_1] = gamma_new_2[idx_2]
        gamma_new_2[idx_2] = temp
        trial_soln = (gamma_new_1, gamma_new_2, curr_soln[2], curr_soln[3])
    else:
        idx = random.randint(0, module_num-1)
        trial_width_dict = module_width_dict.copy()
        trial_height_dict = module_height_dict.copy()
        temp = trial_width_dict[idx]
        trial_width_dict[idx] = trial_height_dict[idx]
        trial_height_dict[idx] = temp
        trial_soln = (curr_soln[0], curr_soln[1], trial_width_dict, trial_height_dict)
    
    trial_cost = cost(trial_soln)
    delta_cost = trial_cost - curr_cost

    if delta_cost < 0:
        curr_cost = trial_cost
        curr_soln = trial_soln
    else:
        r = random.random()
        if r < np.exp(-delta_cost / T):
            curr_cost = trial_cost
            curr_soln = trial_soln

    if trial_cost < min_cost:
        min_cost = trial_cost
        min_soln = copy.deepcopy(trial_soln)
        
    T = T / T_ratio
    if i % 1000 == 0:
        print("T = {:<6e}, curr_cost = {:<6e}, delta_cost = {:<6e}, min_cost = {:<6e}".
              format(T, curr_cost, delta_cost, min_cost))

t_end = time.time()
print("speed = {}/s".format(steps / (t_end - t_start)))
        
"""
pr.disable()
s = io.StringIO()
sortby = SortKey.CUMULATIVE
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())
"""

        
G_H, G_V = constraint_graph(*(min_soln[0:2]))

d_h = longest_path_from_s(G_H, min_soln[2])
d_v = longest_path_from_s(G_V, min_soln[3])

packing_efficiency = sum([min_soln[2][node] * min_soln[3][node] for node in range(module_num)]) / (d_h['t'] * d_v['t'])
print("packing_efficiency = {}".format(packing_efficiency))

draw_packing(d_h, d_v, min_soln[2], min_soln[3])
