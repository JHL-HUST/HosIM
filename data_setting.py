dataset_path = '.\\'
dataset_name = 'Amazon'
# dataset_name = 'DBLP'
dataset_graph = dataset_name + '_graph.pkl'
dataset_filter_community = dataset_name + '_filter_community.pkl'

dataset_seeds = list()
dataset_seed_communities = list()
for i in range(5):
    dataset_seeds.append(dataset_name + '_seed%d.pkl' % (i + 1))
    dataset_seed_communities.append(dataset_name + '_seed_community%d.pkl' % (i + 1))

output_path = 'Results'
output_detected_community = list()
for i in range(len(dataset_seeds)):
    output_detected_community.append('detected_community_%d.pkl' % (i + 1))
output_sampled_graph = "sampled_graph.pkl"
