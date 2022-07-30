import os
import time
import tqdm
import pickle

from data_setting import *
from parameter_setting import *
import parameter_setting
import sample_subgraph
import detect_community


def set_delta(dataset_name):
    if dataset_name == "Amazon":
        parameter_setting.add_threshold = 0.8
        parameter_setting.remove_threshold = 0.2
    elif dataset_name == "DBLP":
        parameter_setting.add_threshold = 0.7
        parameter_setting.remove_threshold = 0.1
    else:
        parameter_setting.add_threshold = 0.3
        parameter_setting.remove_threshold = 0.2
    return

def read_graph_data():
    with open(os.path.join(dataset_path, dataset_name, dataset_graph), 'rb') as gf:
        adjacency_list = pickle.load(gf)
    return adjacency_list

def read_diffusion_information():
    diffusion_path = dataset_name + '_diffusion_r%d_p%d_n%d.pkl' % (pr_hop, pr_steps, maximum_neighbor_number)
    os.makedirs(os.path.join(output_path, dataset_name), exist_ok=True)
    if os.path.exists(os.path.join(output_path, dataset_name, diffusion_path)):
        with open(os.path.join(output_path, dataset_name, diffusion_path), 'rb') as df:
            diffused_nodes, coefficient_nodes = pickle.load(df)
    else:
        diffused_nodes = dict()
        coefficient_nodes = dict()
    return diffused_nodes, coefficient_nodes, diffusion_path

def sample_all_subgraphs(adjacency_list, diffused_nodes, coefficient_nodes):
    sample_path = "ds%d_lf%s_ls%d_in%d_af%s" % (diffusion_size, "T" if lorw_flag else "F", lorw_size, iters_number, str(add_boundary_number) if add_boundary_number is not None else "F")
    os.makedirs(os.path.join(output_path, dataset_name, sample_path), exist_ok=True)
    if os.path.exists(os.path.join(output_path, dataset_name, sample_path, output_sampled_graph)):
        with open(os.path.join(output_path, dataset_name, sample_path, output_sampled_graph), 'rb') as sf:
            sampled_all_subgraphs, sampled_all_cores = pickle.load(sf)
        sample_time = 0
    else:
        sampled_all_subgraphs = dict()
        sampled_all_cores = dict()
        print("Start to sample nodes")
        start_time = time.time()
        sum_nodes = 0
        for i in range(len(dataset_seeds)):
            with open(os.path.join(dataset_path, dataset_name, dataset_seeds[i]), 'rb') as sf:
                query_nodes = pickle.load(sf)
                sum_nodes += len(query_nodes)
            for qn in tqdm.tqdm(query_nodes):
                sampled_all_subgraphs[qn], sampled_all_cores[qn] = sample_subgraph.sample_subgraph(adjacency_list, qn, diffused_nodes, coefficient_nodes)
        sample_time = time.time() - start_time
        print("Average sample time: %.2f" % (sample_time / sum_nodes))
        with open(os.path.join(output_path, dataset_name, sample_path, output_sampled_graph), 'wb') as sf:
            pickle.dump((sampled_all_subgraphs, sampled_all_cores), sf)
    return sampled_all_subgraphs, sampled_all_cores, sample_path, sample_time


def hosim_main():
    set_delta(dataset_name)
    adjacency_list = read_graph_data()
    diffused_nodes, coefficient_nodes, diffusion_path = read_diffusion_information()
    sampled_all_subgraphs, sampled_all_cores, sample_path, sample_time = sample_all_subgraphs(adjacency_list,
                                                                                              diffused_nodes,
                                                                                              coefficient_nodes)
    detect_path = "sf%s_cn%d_at%.1f_rf%s_rt%.1f" % (
    "T" if speedup_flag else "F", components_number, parameter_setting.add_threshold, "T" if remove_flag else "F",
    parameter_setting.remove_threshold)
    os.makedirs(os.path.join(output_path, dataset_name, sample_path, detect_path), exist_ok=True)
    print("Start to detect communities")
    detect_time = 0
    sum_nodes = 0
    for i in range(len(dataset_seeds)):
        with open(os.path.join(dataset_path, dataset_name, dataset_seeds[i]), 'rb') as sf:
            query_nodes = pickle.load(sf)
            sum_nodes += len(query_nodes)
        detected_communities = dict()
        start_time = time.time()
        for qn in tqdm.tqdm(query_nodes):
            detected_communities[qn] = detect_community.detect_multiple_communities(adjacency_list, sampled_all_subgraphs[qn], sampled_all_cores[qn], qn,
                                                                   diffused_nodes, coefficient_nodes)
        detect_time += time.time() - start_time
        with open(os.path.join(output_path, dataset_name, sample_path, detect_path, output_detected_community[i]),
                  'wb') as df:
            pickle.dump(detected_communities, df)
    print("Average detection time: %.2f" % (detect_time / sum_nodes))
    with open(os.path.join(output_path, dataset_name, diffusion_path), 'wb') as df:
        pickle.dump((diffused_nodes, coefficient_nodes), df)
    print("Average time: %.2f" % ((sample_time + detect_time) / sum_nodes))
    return sample_path, detect_path
