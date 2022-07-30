import copy

from parameter_setting import *
import utils
import ppr_cd
from calculate_importance import *


def sample_subgraph(adjacency_list, query_node, diffused_nodes, coefficient_nodes):
    sampled_nodes = diffusion_nodes(adjacency_list, query_node)
    if lorw_flag is True:
        sampled_nodes = lorw_nodes(adjacency_list, sampled_nodes, diffused_nodes, coefficient_nodes)
    core_nodes = copy.deepcopy(sampled_nodes)
    if add_boundary_number is not None and len(core_nodes) <= maximum_sample_subgraph_size:
        for i in range(add_boundary_number):
            sampled_nodes = sampled_nodes.union(utils.get_neighbors_by_coefficient(adjacency_list, sampled_nodes, coefficient_nodes, maximum_sample_subgraph_size - len(sampled_nodes)))
    return sampled_nodes, core_nodes

def diffusion_nodes(adjacency_list, query_node):
    temp_radius = 2
    temp_nodes = set()
    temp_nodes.add(query_node)
    while True:
        temp_nodes = utils.return_ego_nodes(adjacency_list, temp_nodes, radius=temp_radius)
        if len(temp_nodes) < diffusion_size:
            temp_radius = 1
        else:
            break
    if len(temp_nodes) > diffusion_size:
        nodes_probabilities = ppr_cd.ppr_cd(adjacency_list, temp_nodes, [query_node, ], query_node, -1, True)
        node_set = set([np[0] for np in nodes_probabilities[:min(len(nodes_probabilities), int(diffusion_size))]])
        temp_nodes = utils.return_connected_component(adjacency_list, node_set, query_node)
    return temp_nodes

def lorw_nodes(adjacency_list, sample_nodes, diffused_nodes, coefficient_nodes):
    add_number = 0
    while add_number < lorw_size:
        temp_neighbors = utils.get_neighbors_by_coefficient(adjacency_list, sample_nodes, coefficient_nodes, lorw_size)
        temp_add_nodes = list()
        for tn in temp_neighbors:
            sum_inside = 0
            diffuse_node(adjacency_list, tn, diffused_nodes, coefficient_nodes)
            for dn in diffused_nodes[tn]:
                if dn in sample_nodes:
                    sum_inside += diffused_nodes[tn][dn]
            temp_add_nodes.append((tn, sum_inside))
        temp_add_nodes = sorted(temp_add_nodes, key=lambda x: x[1], reverse=True)
        add_nodes_list = [an[0] for an in temp_add_nodes[:min(len(temp_add_nodes), int(lorw_size / iters_number))]]
        sample_nodes = sample_nodes.union(set(add_nodes_list))
        add_number += len(add_nodes_list)
    return sample_nodes
