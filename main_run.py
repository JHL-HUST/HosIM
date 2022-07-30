import random

import data_setting
import hosim_model
import evaluate_community


if __name__ == '__main__':
    random.seed(0)
    print(data_setting.dataset_name)
    sample_path, detect_path = hosim_model.hosim_main()
    evaluate_community.evaluation_run(sample_path, detect_path)
