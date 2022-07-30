import copy
import numpy as np

from parameter_setting import *
import utils


def diffuse_node(adjacency_list, dn, diffused_nodes, coefficient_nodes):
    if dn not in diffused_nodes:
        subgraph_nodes = sample_diffuse_nodes(adjacency_list, dn, coefficient_nodes)
        sorted_nodes = sorted(list(subgraph_nodes))
        node_index = dict()
        for si, sn in enumerate(sorted_nodes):
            node_index[sn] = si
        seed_index = node_index[dn]
        A = generate_adjacency_matrix(adjacency_list, sorted_nodes)
        inverse_degree_array = [1/len(adjacency_list[tn].intersection(subgraph_nodes)) for tn in sorted_nodes]
        inverse_D = np.diag(inverse_degree_array)
        transition_matrix = np.dot(inverse_D, A)
        probability_vector = np.zeros((1, len(sorted_nodes)))
        probability_vector[0, seed_index] = 1
        for i in range(pr_steps):
            probability_vector = np.dot(probability_vector, transition_matrix)
            if probability_vector[0][seed_index] > 0:
                probability_vector += probability_vector[0][seed_index] * transition_matrix[seed_index]
                probability_vector[0][seed_index] = 0
        diffused_nodes[dn] = dict()
        for si, sn in enumerate(sorted_nodes):
            diffused_nodes[dn][sn] = probability_vector[0, si]
    return

def sample_diffuse_nodes(adjacency_list, start_node, coefficient_nodes):
    subgraph_nodes = set()
    subgraph_nodes.add(start_node)
    seed_neighbors = set()
    seed_neighbors.add(start_node)
    for i in range(pr_hop):
        new_neighbors = set()
        for sn in seed_neighbors:
            temp_neighbors = set(pick_nodes_by_coefficient(adjacency_list, sn, coefficient_nodes))
            subgraph_nodes = subgraph_nodes.union(temp_neighbors)
            new_neighbors = new_neighbors.union(temp_neighbors)
        seed_neighbors = copy.deepcopy(new_neighbors)
    return subgraph_nodes

def pick_nodes_by_coefficient(adjacency_list, center_node, coefficient_nodes):
    if maximum_neighbor_number > 0 and len(adjacency_list[center_node]) > maximum_neighbor_number:
        nodes_coefficients = list()
        for tn in adjacency_list[center_node]:
            if tn not in coefficient_nodes:
                coefficient_nodes[tn] = utils.calculate_clustering(adjacency_list, tn)
            nodes_coefficients.append([tn, coefficient_nodes[tn]])
        nodes_coefficients = sorted(nodes_coefficients, key=lambda x: x[1], reverse=True)
        node_set = set([tn[0] for tn in nodes_coefficients[:maximum_neighbor_number]])
        return node_set
    else:
        return adjacency_list[center_node]

def generate_adjacency_matrix(adjacency_list, sorted_nodes):
    A = np.zeros((len(sorted_nodes), len(sorted_nodes))).astype(np.float16)
    for i, u in enumerate(sorted_nodes):
        for j, v in enumerate(sorted_nodes):
            if v in adjacency_list[u]:
                A[i][j] = 1
    return A
