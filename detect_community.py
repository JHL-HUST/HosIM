from parameter_setting import *
import parameter_setting
import ppr_cd
from calculate_importance import *
import utils


def detect_multiple_communities(adjacency_list, sampled_all_nodes, sampled_core_nodes, query_node, diffused_nodes, coefficient_nodes):
    detected_communities = list()
    node_importances, nodes_weights = count_diffusion_information(adjacency_list, sampled_all_nodes, sampled_core_nodes, diffused_nodes, coefficient_nodes)
    seeds_sets = find_seeds_sets(query_node, node_importances)
    if len(seeds_sets) > 0:
        seed_components = utils.return_subgraph_connected_components(adjacency_list, seeds_sets)
        if len(seed_components) > components_number:
            seed_components = pick_components(seed_components, nodes_weights)
        for sc in seed_components:
            dc = detect_community(adjacency_list, sampled_all_nodes, nodes_weights, set(sc), query_node, sampled_core_nodes)
            if query_node in dc:
                detected_communities.append(dc)
    if len(detected_communities) == 0:
        dc = ppr_cd.ppr_cd(adjacency_list, sampled_all_nodes, [query_node, ], query_node)
        if query_node in dc:
            detected_communities.append(dc)
        else:
            detected_communities.append([query_node, ])
    detected_communities = add_more_nodes(adjacency_list, sampled_all_nodes, detected_communities, diffused_nodes, coefficient_nodes)
    if remove_flag is True:
        detected_communities = remove_nodes(adjacency_list, detected_communities, diffused_nodes, coefficient_nodes)
    return detected_communities

def count_diffusion_information(adjacency_list, sampled_all_nodes, sampled_core_nodes, diffused_nodes, coefficient_nodes):
    node_importances = list()
    node_weights = dict()
    if speedup_flag is True:
        nodes_coefficients = list()
        for ns in sampled_core_nodes:
            if ns not in coefficient_nodes:
                coefficient_nodes[ns] = utils.calculate_clustering(adjacency_list, ns)
            nodes_coefficients.append([ns, coefficient_nodes[ns]])
        nodes_coefficients = sorted(nodes_coefficients, key=lambda x: x[1], reverse=True)
        nodes_coefficients = nodes_coefficients[:lorw_size]
        candidate_nodes = [tn[0] for tn in nodes_coefficients]
    else:
        candidate_nodes = sampled_core_nodes
    for ns in candidate_nodes:
        node_importances.append([ns, count_importance(adjacency_list, sampled_all_nodes, ns, diffused_nodes, coefficient_nodes)])
        node_weights[ns] = node_importances[-1][1]
    node_importances = sorted(node_importances, key=lambda x: x[1], reverse=True)
    return node_importances, node_weights

def count_importance(adjacency_list, sampled_all_nodes, center_node, diffused_nodes, coefficient_nodes):
    temp_set = set()
    temp_set.add(center_node)
    temp_nodes = utils.return_subgraph_ego_nodes(adjacency_list, sampled_all_nodes, temp_set, radius=pr_hop)
    if len(temp_nodes) > maximum_diffusion_subgraph_size:
        temp_coefficient = list()
        for tn in temp_nodes:
            if tn not in coefficient_nodes:
                coefficient_nodes[tn] = utils.calculate_clustering(adjacency_list, tn)
            temp_coefficient.append([tn, coefficient_nodes[tn]])
        temp_coefficient = sorted(temp_coefficient, key=lambda x: x[1], reverse=True)
        temp_nodes = set([tc[0] for tc in temp_coefficient[:maximum_diffusion_subgraph_size]])
    sum_importance = 0
    for tn in temp_nodes:
        if tn == center_node:
            continue
        diffuse_node(adjacency_list, tn, diffused_nodes, coefficient_nodes)
        if center_node in diffused_nodes[tn]:
            sum_importance += diffused_nodes[tn][center_node]
    return sum_importance

def find_seeds_sets(query_node, node_importances):
    bigger_nodes = set()
    for ni in node_importances:
        if ni[0] != query_node:
            bigger_nodes.add(ni[0])
        else:
            return bigger_nodes
    return bigger_nodes

def pick_components(seeds_components, nodes_weights):
    components_importance = list()
    for sc in seeds_components:
        importance_sum = 0
        for tn in sc:
            if tn in nodes_weights:
                importance_sum += nodes_weights[tn]
        components_importance.append((list(sc), importance_sum))
    components_importance = sorted(components_importance, key=lambda x: x[1], reverse=True)
    return [ci[0] for ci in components_importance[:components_number]]

def detect_community(adjacency_list, sampled_all_nodes, nodes_weights, seed_nodes, query_node, sampled_core_nodes):
    center_node = find_important_node(seed_nodes, nodes_weights)
    if all_shortest_flag is True:
        seed_set = seed_nodes.union(find_important_path(adjacency_list, sampled_core_nodes, nodes_weights, query_node, center_node))
    else:
        seed_set = seed_nodes.union(utils.return_single_shortest_path(adjacency_list, sampled_core_nodes, query_node, center_node))
    detected_community = ppr_cd.ppr_cd(adjacency_list, sampled_all_nodes, seed_set, query_node, center_node)
    return detected_community

def find_important_node(seed_nodes, nodes_weights):
    max_weight = -1
    max_node = -1
    for sn in seed_nodes:
        if nodes_weights[sn] > max_weight:
            max_weight = nodes_weights[sn]
            max_node = sn
    return max_node

def find_important_path(adjacency_list, sampled_core_nodes, nodes_weights, query_node, center_node):
    max_weight = -1
    max_path = -1
    for ap in utils.return_all_shortest_paths(adjacency_list, sampled_core_nodes, query_node, center_node):
        sum_weight = 0
        for tn in ap:
            if tn in nodes_weights:
                sum_weight += nodes_weights[tn]
        if sum_weight > max_weight:
            max_weight = sum_weight
            max_path = ap
    seed_set = set(max_path)
    temp_set = set()
    temp_set.add(center_node)
    seed_set = seed_set.union(utils.return_subgraph_ego_nodes(adjacency_list, sampled_core_nodes, temp_set, radius=1))
    return seed_set

def add_more_nodes(adjacency_list, sampled_all_nodes, detected_communities, diffused_nodes, coefficient_nodes):
    new_communities = list()
    for dc in detected_communities:
        while True:
            new_add_nodes = set()
            temp_neighbors = utils.get_subgraph_neighbors_by_coefficient(adjacency_list, sampled_all_nodes, dc, coefficient_nodes, -1)
            for tn in temp_neighbors:
                if tn in dc:
                    continue
                sum_inside = 0
                diffuse_node(adjacency_list, tn, diffused_nodes, coefficient_nodes)
                for dn in diffused_nodes[tn]:
                    if dn in dc:
                        sum_inside += diffused_nodes[tn][dn]
                if sum_inside >= parameter_setting.add_threshold:
                    new_add_nodes.add(tn)
            if len(new_add_nodes) == 0:
                break
            else:
                dc = set(dc).union(new_add_nodes)
        new_communities.append(dc)
    return new_communities

def remove_nodes(adjacency_list, detected_communities, diffused_nodes, coefficient_nodes):
    new_communities = list()
    for dc in detected_communities:
        while True:
            removed_nodes = set()
            for tn in dc:
                diffuse_node(adjacency_list, tn, diffused_nodes, coefficient_nodes)
                sum_inside = 0
                for dn in diffused_nodes[tn]:
                    if dn in dc:
                        sum_inside += diffused_nodes[tn][dn]
                if sum_inside < parameter_setting.remove_threshold:
                    removed_nodes.add(tn)
            if len(removed_nodes) == 0:
                break
            else:
                dc = set(dc).difference(removed_nodes)
        new_communities.append(dc)
    return new_communities
