import sys, os, re, subprocess
from datetime import datetime

result_stem = sys.argv[1]
experiment = sys.argv[2]
model_class = "KF_SIGMA_DDM" # indicate if 'KF_UCB', 'RL', or 'KF_UCB_DDM' model

current_datetime = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
result_stem = f"{result_stem}_{current_datetime}/"

ssub_path = '/media/labs/rsmith/lab-members/cgoldman/Wellbeing/social_media/VB_scripts/run_social.ssub'

subject_list_path = '/media/labs/rsmith/lab-members/cgoldman/Wellbeing/social_media/social_media_prolific_IDs.csv'
subjects = []
with open(subject_list_path) as infile:
    for line in infile:
        subjects.append(line.strip())

if model_class=="KF_UCB":
    models = [
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r'},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,info_bonus'},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,baseline_info_bonus'},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,random_exp'},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,reward_sensitivity'},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,info_bonus,baseline_info_bonus'}, 
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,info_bonus,random_exp'}, # winner for dislike (same as when sigma d is included)
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,info_bonus,reward_sensitivity'},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,baseline_info_bonus,random_exp'},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,baseline_info_bonus,reward_sensitivity'},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,random_exp,reward_sensitivity'},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,info_bonus,baseline_info_bonus,random_exp'},  # winner for like (same as when sigma d is included)
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,info_bonus,baseline_info_bonus,reward_sensitivity'},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,info_bonus,random_exp,reward_sensitivity'},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,baseline_info_bonus,random_exp,reward_sensitivity'},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,info_bonus,baseline_info_bonus,random_exp,reward_sensitivity'},

        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,DE_RE_horizon'},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,DE_RE_horizon,baseline_info_bonus'},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,DE_RE_horizon,reward_sensitivity'},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,DE_RE_horizon,baseline_info_bonus,reward_sensitivity'},
    ]
elif model_class == "RL":
    models = [
        {'field': 'learning_rate,baseline_noise,side_bias,baseline_info_bonus,info_bonus,random_exp,associability_weight,initial_associability'},
        {'field': 'learning_rate_pos,learning_rate_neg,baseline_noise,side_bias,baseline_info_bonus,info_bonus,random_exp'},
        {'field': 'learning_rate,baseline_noise,side_bias,baseline_info_bonus,info_bonus,random_exp'},
        {'field': 'learning_rate,baseline_noise,side_bias,baseline_info_bonus,DE_RE_horizon,associability_weight,initial_associability'},
        {'field': 'learning_rate_pos,learning_rate_neg,baseline_noise,side_bias,baseline_info_bonus,DE_RE_horizon'},
        {'field': 'learning_rate,baseline_noise,side_bias,baseline_info_bonus,DE_RE_horizon'}, # winning RL model for like and dislike
    ]
# Since winning KF_UCB models (for like and dislike) beat winning RL model,
# we take winning KF_UCB models and add DDM parameters
elif model_class=="KF_UCB_DDM":
    models = [
        # Action probability maps to drift rate
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,decision_thresh_baseline,starting_bias_baseline,drift_baseline,info_bonus,random_exp,baseline_info_bonus,drift_action_prob_mod', 'drift_mapping': 'action_prob','bias_mapping': '', 'thresh_mapping': ''},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,decision_thresh_baseline,starting_bias_baseline,drift_baseline,info_bonus,random_exp,drift_action_prob_mod', 'drift_mapping': 'action_prob','bias_mapping': '', 'thresh_mapping': ''},
        # Action probability maps to starting bias
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,decision_thresh_baseline,starting_bias_baseline,drift_baseline,info_bonus,random_exp,baseline_info_bonus,starting_bias_action_prob_mod', 'drift_mapping': '','bias_mapping': 'action_prob', 'thresh_mapping': ''},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,decision_thresh_baseline,starting_bias_baseline,drift_baseline,info_bonus,random_exp,starting_bias_action_prob_mod', 'drift_mapping': '','bias_mapping': 'action_prob', 'thresh_mapping': ''},
        # Action probability maps to decision threshold
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,decision_thresh_baseline,starting_bias_baseline,drift_baseline,info_bonus,random_exp,baseline_info_bonus,decision_thresh_action_prob_mod', 'drift_mapping': '','bias_mapping': '', 'thresh_mapping': 'action_prob'},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,decision_thresh_baseline,starting_bias_baseline,drift_baseline,info_bonus,random_exp,decision_thresh_action_prob_mod', 'drift_mapping': '','bias_mapping': '', 'thresh_mapping': 'action_prob'},

        # Reward difference maps to drift rate, side bias/UCB difference maps to starting bias, decision noise maps to decision threshold
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,decision_thresh_baseline,starting_bias_baseline,drift_baseline,info_bonus,random_exp,baseline_info_bonus,drift_reward_diff_mod,starting_bias_UCB_diff_mod', 'drift_mapping': 'reward_diff','bias_mapping': 'side_bias,UCB_diff', 'thresh_mapping': 'decision_noise'},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,decision_thresh_baseline,starting_bias_baseline,drift_baseline,info_bonus,random_exp,drift_reward_diff_mod,starting_bias_UCB_diff_mod', 'drift_mapping': 'reward_diff','bias_mapping': 'side_bias,UCB_diff', 'thresh_mapping': 'decision_noise'},
        # Reward difference maps to starting bias, side bias/UCB difference maps to drift rate, decision noise maps to decision threshold
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,decision_thresh_baseline,starting_bias_baseline,drift_baseline,info_bonus,random_exp,baseline_info_bonus,starting_bias_reward_diff_mod,drift_UCB_diff_mod', 'drift_mapping': 'side_bias,UCB_diff','bias_mapping': 'reward_diff', 'thresh_mapping': 'decision_noise'},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,decision_thresh_baseline,starting_bias_baseline,drift_baseline,info_bonus,random_exp,starting_bias_reward_diff_mod,drift_UCB_diff_mod', 'drift_mapping': 'side_bias,UCB_diff','bias_mapping': 'reward_diff', 'thresh_mapping': 'decision_noise'},

        # Reward difference/side bias/UCB difference maps to drift rate, decision noise maps to decision threshold
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,decision_thresh_baseline,starting_bias_baseline,drift_baseline,info_bonus,random_exp,baseline_info_bonus,drift_reward_diff_mod,drift_UCB_diff_mod', 'drift_mapping': 'reward_diff,side_bias,UCB_diff','bias_mapping': '', 'thresh_mapping': 'decision_noise'},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,decision_thresh_baseline,starting_bias_baseline,drift_baseline,info_bonus,random_exp,drift_reward_diff_mod,drift_UCB_diff_mod', 'drift_mapping': 'reward_diff,side_bias,UCB_diff','bias_mapping': '', 'thresh_mapping': 'decision_noise'},
        # Reward difference/side bias/UCB difference maps to starting bias, decision noise maps to decision threshold
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,decision_thresh_baseline,starting_bias_baseline,drift_baseline,info_bonus,random_exp,baseline_info_bonus,starting_bias_reward_diff_mod,starting_bias_UCB_diff_mod', 'drift_mapping': '','bias_mapping': 'reward_diff,side_bias,UCB_diff', 'thresh_mapping': 'decision_noise'},
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,decision_thresh_baseline,starting_bias_baseline,drift_baseline,info_bonus,random_exp,starting_bias_reward_diff_mod,starting_bias_UCB_diff_mod', 'drift_mapping': '','bias_mapping': 'reward_diff,side_bias,UCB_diff', 'thresh_mapping': 'decision_noise'},
    ]

elif model_class=="KF_SIGMA_DDM":
    models = [
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,info_bonus,baseline_info_bonus,drift_reward_diff_mod,decision_thresh_baseline,random_exp', 'drift_mapping': 'reward_diff,decision_noise','bias_mapping': 'info_diff,side_bias', 'thresh_mapping': ''},
    ]

elif model_class=="KF_SIGMA":
    models = [
        {'field': 'sigma_d,baseline_noise,side_bias,sigma_r,info_bonus,baseline_info_bonus,random_exp', 'drift_mapping': 'reward_diff,decision_noise','bias_mapping': 'info_diff,side_bias', 'thresh_mapping': ''},
    ]


room_type = ["Like", "Dislike"]

for room in room_type:
    # if room == "Like":
    #     continue
    results = result_stem + room + "/"

    for index, model in enumerate(models, start=1):
        # i = 0
        combined_results_dir = os.path.join(results, f"model{index}/")
        field = model['field']
        # return empty string if not found
        drift_mapping = model.get('drift_mapping', '')
        bias_mapping = model.get('bias_mapping', '')
        thresh_mapping = model.get('thresh_mapping', '')
        
        if not os.path.exists(combined_results_dir):
            os.makedirs(combined_results_dir)
            print(f"Created results directory {combined_results_dir}")

        if not os.path.exists(f"{combined_results_dir}/logs"):
            os.makedirs(f"{combined_results_dir}/logs")
            print(f"Created results-logs directory {combined_results_dir}/logs")
        for subject in subjects:
            
            stdout_name = f"{combined_results_dir}/logs/SM-{model_class}-model_{index}-{room}_room-{subject}-%J.stdout"
            stderr_name = f"{combined_results_dir}/logs/SM-{model_class}-model_{index}-{room}_room-{subject}-%J.stderr"
            jobname = f'SM-{model_class}-model_{index}-{room}_room-{subject}'
            
            drift_map = drift_mapping if drift_mapping else "none"
            bias_map = bias_mapping if bias_mapping else "none"
            thresh_map = thresh_mapping if thresh_mapping else "none"
            os.system(f"sbatch -J {jobname} -o {stdout_name} -e {stderr_name} {ssub_path} {subject} {combined_results_dir} {room} {experiment} {field} {model_class} {drift_map} {bias_map} {thresh_map}")

            print(f"SUBMITTED JOB [{jobname}]")
            # i = i+1
            # if i ==2:
            #     break


# python3 /media/labs/rsmith/lab-members/cgoldman/Wellbeing/social_media/VB_scripts/runall_social.py /media/labs/rsmith/lab-members/cgoldman/Wellbeing/social_media/output/SM_fits_KF_SIGMA_DDM_model "prolific"