import os
import pickle
import tqdm
import pandas as pd

from data_setting import *


def F1_score(detected_communities, ground_truth_communities):
    precision = calculate_precision(detected_communities, ground_truth_communities)
    recall = calculate_recall(detected_communities, ground_truth_communities)
    if precision + recall == 0:
        return 0, 0, 0
    f1 = 2 * precision * recall / (precision + recall)
    return precision, recall, f1

def calculate_precision(detected_communities, ground_truth_communities):
    sum_pre = 0
    for dc in detected_communities:
        max_compare = -1
        for gt in ground_truth_communities:
            common_number = len(set(dc).intersection(set(gt)))
            union_number = len(set(dc).union(set(gt)))
            compare_value = common_number / union_number
            if compare_value > max_compare:
                max_compare = compare_value
        sum_pre += max_compare
    return sum_pre / len(detected_communities)

def calculate_recall(detected_communities, ground_truth_communities):
    sum_rec = 0
    for gt in ground_truth_communities:
        max_compare = -1
        for dc in detected_communities:
            common_number = len(set(dc).intersection(set(gt)))
            union_number = len(set(dc).union(set(gt)))
            compare_value = common_number / union_number
            if compare_value > max_compare:
                max_compare = compare_value
        sum_rec += max_compare
    return sum_rec / len(ground_truth_communities)


def evaluation_run(sample_path, detect_path):
    print("Start to evaluate communities")
    df = pd.DataFrame(columns=["f1_score", "precision", "recall", "seed_name"])
    for data_index in range(len(dataset_seeds)):
        gt_path = os.path.join(dataset_path, dataset_name, dataset_seed_communities[data_index])
        dc_path = os.path.join(output_path, dataset_name, sample_path, detect_path, output_detected_community[data_index])
        with open(gt_path, 'rb') as gf:
            seed_communities = pickle.load(gf)
        with open(dc_path, 'rb') as sf:
            all_detected_communities = pickle.load(sf)
        sum_pre = 0.0
        sum_recall = 0.0
        sum_f1 = 0.0
        for sd in tqdm.tqdm(seed_communities):
            ground_truth_communities = seed_communities[sd]
            detected_communities = all_detected_communities[sd]
            precision, recall, f1 = F1_score(detected_communities, ground_truth_communities)
            sum_pre += precision
            sum_recall += recall
            sum_f1 += f1
        temp_series = pd.Series([str(sum_f1 / len(seed_communities)), str(sum_pre / len(seed_communities)),
                                 str(sum_recall / len(seed_communities)), str(dataset_seeds[data_index])],
                                index=["f1_score", "precision", "recall", "seed_name"])
        df = df.append(temp_series, ignore_index=True)
    df.to_excel(os.path.join(output_path, dataset_name, sample_path, detect_path, "evaluation_community.xlsx"), encoding="utf-8")
