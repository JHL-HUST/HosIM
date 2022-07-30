import copy
import random


def return_ego_nodes(adjacency_list, seed_nodes, radius=1):
    all_nodes = copy.deepcopy(seed_nodes)
    new_nodes = copy.deepcopy(seed_nodes)
    for i in range(radius):
        temp_nodes = set()
        for nn in new_nodes:
            temp_nodes = temp_nodes.union(adjacency_list[nn])
        new_nodes = temp_nodes.difference(all_nodes)
        all_nodes = all_nodes.union(new_nodes)
    return all_nodes

def return_subgraph_ego_nodes(adjacency_list, subgraph_nodes, seed_nodes, radius=1):
    all_nodes = copy.deepcopy(seed_nodes)
    new_nodes = copy.deepcopy(seed_nodes)
    for i in range(radius):
        temp_nodes = set()
        for nn in new_nodes:
            temp_nodes = temp_nodes.union(adjacency_list[nn].intersection(subgraph_nodes))
        new_nodes = temp_nodes.difference(all_nodes)
        all_nodes = all_nodes.union(new_nodes)
    return all_nodes

def return_connected_component(adjacency_list, node_set, query_node):
    component_nodes = set()
    component_nodes.add(query_node)
    while True:
        before_size = len(component_nodes)
        temp_nodes = set()
        for cn in component_nodes:
            temp_nodes = temp_nodes.union(adjacency_list[cn])
        temp_nodes = temp_nodes.intersection(node_set)
        component_nodes = component_nodes.union(temp_nodes)
        if len(component_nodes) == before_size:
            break
    return component_nodes

def return_subgraph_connected_components(adjacency_list, node_set):
    remaining_nodes = copy.deepcopy(node_set)
    all_components = list()
    while len(remaining_nodes) > 0:
        temp_component = set()
        random_node = remaining_nodes.pop()
        temp_component.add(random_node)
        new_nodes = set()
        new_nodes.add(random_node)
        while True:
            before_size = len(temp_component)
            temp_nodes = set()
            for nn in new_nodes:
                temp_nodes = temp_nodes.union(adjacency_list[nn].intersection(node_set))
            new_nodes = temp_nodes.difference(temp_component)
            temp_component = temp_component.union(new_nodes)
            if len(temp_component) == before_size:
                break
        all_components.append(temp_component)
        remaining_nodes = remaining_nodes.difference(temp_component)
    return all_components

def get_neighbors_by_coefficient(adjacency_list, sampled_nodes, coefficient_nodes, maximum_size):
    neighbors_nodes = set()
    for tsn in sampled_nodes:
        for tn in adjacency_list[tsn]:
            if tn not in sampled_nodes:
                neighbors_nodes.add(tn)
    if maximum_size > 0 and len(neighbors_nodes) > maximum_size:
        temp_coefficient = list()
        for tn in neighbors_nodes:
            if tn not in coefficient_nodes:
                coefficient_nodes[tn] = calculate_clustering(adjacency_list, tn)
            temp_coefficient.append([tn, coefficient_nodes[tn]])
        temp_coefficient = sorted(temp_coefficient, key=lambda x: x[1], reverse=True)
        neighbors_nodes = set([tc[0] for tc in temp_coefficient[:maximum_size]])
    return neighbors_nodes

def get_subgraph_neighbors_by_coefficient(adjacency_list, subgraph_nodes, sampled_nodes, coefficient_nodes, maximum_size):
    neighbors_nodes = set()
    for tsn in sampled_nodes:
        for tn in adjacency_list[tsn]:
            if tn in subgraph_nodes and tn not in sampled_nodes:
                neighbors_nodes.add(tn)
    if maximum_size > 0 and len(neighbors_nodes) > maximum_size:
        temp_coefficient = list()
        for tn in neighbors_nodes:
            if tn not in coefficient_nodes:
                coefficient_nodes[tn] = calculate_clustering(adjacency_list, tn)
            temp_coefficient.append([tn, coefficient_nodes[tn]])
        temp_coefficient = sorted(temp_coefficient, key=lambda x: x[1], reverse=True)
        neighbors_nodes = set([tc[0] for tc in temp_coefficient[:maximum_size]])
    return neighbors_nodes

def calculate_clustering(adjacency_list, query_node):
    neighbor_nodes = adjacency_list[query_node]
    if len(neighbor_nodes) == 1:
        return 1
    number_edges = 0
    for tn in neighbor_nodes:
        number_edges += len(adjacency_list[tn].intersection(neighbor_nodes))
    return number_edges / (2 * len(neighbor_nodes) * (len(neighbor_nodes) - 1))

def return_single_shortest_path(adjacency_list, subgraph_nodes, start_node, end_node):
    hop_nodes = get_hop_nodes(adjacency_list, subgraph_nodes, start_node, end_node)
    path_nodes = set()
    path_nodes.add(end_node)
    last_node = end_node
    for i in range(len(hop_nodes)-1, -1, -1):
        last_node = random.choice(adjacency_list[last_node].intersection(hop_nodes[i]))
        path_nodes.add(last_node)
    return path_nodes

def return_all_shortest_paths(adjacency_list, subgraph_nodes, start_node, end_node):
    hop_nodes = get_hop_nodes(adjacency_list, subgraph_nodes, start_node, end_node)
    all_paths = list()
    temp_path = list()
    temp_path.append(end_node)
    add_nodes_from_layers(adjacency_list, hop_nodes, len(hop_nodes)-1, temp_path, all_paths, start_node)
    return all_paths

def add_nodes_from_layers(adjacency_list, hop_nodes, hop_iter, temp_path, all_paths, start_node):
    if hop_iter == 0:
        temp_path.append(start_node)
        all_paths.append(copy.deepcopy(temp_path))
        return
    last_node = temp_path[-1]
    last_neighbors = adjacency_list[last_node].intersection(hop_nodes[hop_iter])
    for ln in last_neighbors:
        temp_path.append(ln)
        add_nodes_from_layers(adjacency_list, hop_nodes, hop_iter-1, temp_path, all_paths, start_node)
        temp_path.pop()
    return

def get_hop_nodes(adjacency_list, subgraph_nodes, start_node, end_node):
    hop_nodes = list()
    temp_set = set()
    temp_set.add(start_node)
    hop_nodes.append(temp_set)
    new_nodes = copy.deepcopy(temp_set)
    all_nodes = copy.deepcopy(temp_set)
    while True:
        temp_nodes = set()
        find_flag = False
        for nn in new_nodes:
            temp_neighbors = adjacency_list[nn]
            if end_node in temp_neighbors:
                find_flag = True
                break
            temp_nodes = temp_nodes.union(adjacency_list[nn].intersection(subgraph_nodes))
        if find_flag == True:
            break
        new_nodes = temp_nodes.difference(all_nodes)
        hop_nodes.append(new_nodes)
        all_nodes = all_nodes.union(new_nodes)
    return hop_nodes
