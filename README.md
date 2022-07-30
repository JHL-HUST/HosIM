HoSIM: Higher-order Structural Importance based Method for Multiple Local Community Detection
===============================================

About
-----

A powerful method for multiple local community detection based on higher-order structural importance, named HoSIM. HoSIM utilizes two new metrics to evaluate the HoSI score of a subgraph to a node and the HoSI score of a node, where the first metric is used to judge whether the node belongs to the community structure, and the second metric estimates whether there exist dense structures around the node. Then, HoSIM enforces a three-stage processing, namely subgraph sampling, core member identification, and local community detection. The key idea is utilizing HoSI to find and identify the core members of communities relevant to the query node and optimize the generated communities.


The descriptions of python files
----------------------------

* calculate_importance.py: calculate the higher-order structural importance
* data_setting.py: dataset setting
* detect_community.py: detect local communities
* evaluate_community.py: evaluate detected communities by using F1-score
* hosim_model.py: HoSIM model
* main_run.py: run HoSIM
* parameter_setting.py: parameter setting
* ppr_cd.py: PRN algorithm
* preprocess_data.py: remove copies from original communities and select seeds (you should run this python file first, and then run "main_run.py")
* sample_subgraph.py: sample subgraphs
* utils.py: util algorithms


How to use your own datasets
----------------------------

You can create a new folder and copy the graph data as well as the community data into the folder. Note that, you should also change the corresponding variables in "data_setting.py". 

The detection results are generated in the folder of "Results", and you can open an excel file "evaluation_community.xlsx" to check the F1-socre.
