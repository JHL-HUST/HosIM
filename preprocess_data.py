import os
import tqdm
import pickle
import random


dataset_names = ['Amazon', 'DBLP']
overlapping_number = 5
seed_size = 100
minimum_size = 1
maximum_size = 999999
filter_percents = -1
identity_flag = True


def read_graph(graph_name, output_graph):
    adjacency_list = dict()
    number_edges = 0
    with open(graph_name, 'r') as gn:
        for node_pair in tqdm.tqdm(gn.readlines()):
            if node_pair[0] == '#':
                continue
            number_edges += 1
            node_pair = node_pair.strip().split()
            first_node = int(node_pair[0])
            second_node = int(node_pair[1])
            add_edge_to_al(adjacency_list, first_node, second_node)
            add_edge_to_al(adjacency_list, second_node, first_node)
    print("Number of nodes: %d" % (len(adjacency_list)))
    print("Number of edges: %d" % (number_edges))
    with open(output_graph, 'wb') as og:
        pickle.dump(adjacency_list, og)
    return adjacency_list

def add_edge_to_al(adjacency_list, first_node, second_node):
    if first_node not in adjacency_list:
        adjacency_list[first_node] = set()
    adjacency_list[first_node].add(second_node)
    return

def read_communities(adjacency_list, community_name, output_community):
    with open(community_name, 'r') as cn:
        community_data = list()
        for each_community in tqdm.tqdm(cn.readlines()):
            temp_community = set()
            for tc in each_community.strip().split():
                tc = int(tc)
                temp_community.add(tc)
            if len(temp_community) < minimum_size or len(temp_community) > maximum_size:
                continue
            if identity_flag is True:
                exist_flag = False
                for pc in community_data:
                    if pc == temp_community:
                        exist_flag = True
                        break
                if exist_flag is True:
                    continue
            community_data.append(temp_community)
    print("Number of communities: %d" % (len(community_data)))
    if filter_percents > 0:
        community_data = sorted(community_data, key=lambda x: len(x), reverse=False)
        border_number = int(len(community_data) * filter_percents)
        while True:
            if border_number + 1 < len(community_data) and len(community_data[border_number]) == len(community_data[border_number + 1]):
                border_number += 1
            else:
                break
        community_data = community_data[:border_number + 1]
        print(len(community_data))
    with open(output_community, 'wb') as oc:
        pickle.dump(community_data, oc)
    count_community_attribute(adjacency_list, community_data)
    return community_data

def count_community_attribute(adjacency_list, community_data):
    largest_size = 0
    sum_sizes = 0
    sum_mu = 0
    for cm in community_data:
        if len(cm) > largest_size:
            largest_size = len(cm)
        sum_sizes += len(cm)
        sum_mu += calculate_mu(adjacency_list, cm)
    print("Largest size: %d" % (largest_size))
    print("Average size: %.2f" % (sum_sizes / len(community_data)))
    print("Average mu: %.2f" % (sum_mu / len(community_data)))
    return

def calculate_mu(adjacency_list, community):
    sum_mu = 0
    for cn in community:
        out_degree = len(adjacency_list[cn]) - len(adjacency_list[cn].intersection(community))
        sum_mu += out_degree / len(adjacency_list[cn])
    return sum_mu / len(community)

def count_community_information(community_data):
    node_community = dict()
    number_node = dict()
    for ci, cd in enumerate(community_data):
        for tn in cd:
            if tn not in node_community:
                node_community[tn] = list()
            node_community[tn].append(ci)
    for nc in node_community:
        if len(node_community[nc]) not in number_node:
            number_node[len(node_community[nc])] = list()
        number_node[len(node_community[nc])].append(nc)
    return node_community, number_node

def store_seed_communities(query_nodes, node_community, community_data, output_seed_community):
    seed_communities = dict()
    for qn in query_nodes:
        community_indexs = node_community[qn]
        seed_communities[qn] = list()
        for ci in community_indexs:
            seed_communities[qn].append(community_data[ci])
    with open(output_seed_community, 'wb') as pf:
        pickle.dump(seed_communities, pf)
    return


def main(dataset_name):
    print(dataset_name)
    random.seed(0)
    graph_name = os.path.join(dataset_name, dataset_name+'_graph.txt')
    output_graph = os.path.join(dataset_name, dataset_name+'_graph.pkl')
    graph_data = read_graph(graph_name, output_graph)
    community_name = os.path.join(dataset_name, dataset_name+'_community.txt')
    output_community = os.path.join(dataset_name, dataset_name+'_filter_community.pkl')
    community_data = read_communities(graph_data, community_name, output_community)
    node_community, number_node = count_community_information(community_data)
    for on in range(overlapping_number):
        query_nodes = random.sample(number_node[on + 1], min(seed_size, len(number_node[on + 1])))
        print("Overlapping %d number is: %d" % (on+1, len(number_node[on + 1])))
        with open(os.path.join(dataset_name, dataset_name+('_seed%d.pkl') % (on+1)), 'wb') as pf:
            pickle.dump(query_nodes, pf)
        store_seed_communities(query_nodes, node_community, community_data, os.path.join(dataset_name, dataset_name+('_seed_community%d.pkl') % (on+1)))


if __name__ == '__main__':
    for dn in dataset_names:
        main(dn)
