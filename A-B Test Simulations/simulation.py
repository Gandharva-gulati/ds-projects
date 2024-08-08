import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)
import pdb; pdb.set_trace();
# Parameters
start_date = datetime(2023, 1, 1)
duration_days = 30
total_users = 10000

# Control group parameters
control_ctr = 0.05
control_cr = 0.02
control_aov_mean = 50
control_aov_std = 20

# Treatment group parameters (slight improvements)
treatment_ctr = 0.06
treatment_cr = 0.025
treatment_aov_mean = 55
treatment_aov_std = 22

# Create users DataFrame
users = pd.DataFrame({
    'user_id': range(total_users),
    'group': ['control'] * (total_users // 2) + ['treatment'] * (total_users // 2),
    'clicks': 0,
    'purchases': 0,
    'total_spent': 0.0
})

# Function to simulate user journey
def simulate_user_journey(row):
    if row['group'] == 'control':
        ctr, cr, aov_mean, aov_std = control_ctr, control_cr, control_aov_mean, control_aov_std
    else:
        ctr, cr, aov_mean, aov_std = treatment_ctr, treatment_cr, treatment_aov_mean, treatment_aov_std
    
    if np.random.random() < ctr:
        row['clicks'] += 1
        if np.random.random() < cr:
            row['purchases'] += 1
            row['total_spent'] += max(0, np.random.normal(aov_mean, aov_std))
    return row

# Function to simulate a day
def simulate_day(users):
    users = users.apply(lambda row: simulate_user_journey(row) if np.random.random() < 0.1 else row, axis=1)
    return users

# Run simulation
current_date = start_date
while current_date <= start_date + timedelta(days=duration_days):
    users = simulate_day(users)
    current_date += timedelta(days=1)

# Get results
results = users.groupby('group').agg({
    'user_id': 'count',
    'clicks': 'sum',
    'purchases': 'sum',
    'total_spent': 'sum'
}).rename(columns={'user_id': 'users'})

results['ctr'] = results['clicks'] / results['users']
results['cr'] = results['purchases'] / results['clicks']
results['aov'] = results['total_spent'] / results['purchases']

# Analyze results
def analyze_results(results):
    for metric in ['ctr', 'cr', 'aov']:
        control_value = results.loc['control', metric]
        treatment_value = results.loc['treatment', metric]
        relative_improvement = (treatment_value - control_value) / control_value
        
        print(f"\n{metric.upper()} Analysis:")
        print(f"Control: {control_value:.4f}")
        print(f"Treatment: {treatment_value:.4f}")
        print(f"Relative Improvement: {relative_improvement:.2%}")
        
        # Perform statistical test
        if metric in ['ctr', 'cr']:
            # Use Chi-square test for rates
            control_successes = results.loc['control', 'clicks' if metric == 'ctr' else 'purchases']
            control_trials = results.loc['control', 'users' if metric == 'ctr' else 'clicks']
            treatment_successes = results.loc['treatment', 'clicks' if metric == 'ctr' else 'purchases']
            treatment_trials = results.loc['treatment', 'users' if metric == 'ctr' else 'clicks']
            
            chi2, p_value = stats.chi2_contingency([
                [control_successes, control_trials - control_successes],
                [treatment_successes, treatment_trials - treatment_successes]
            ])[:2]
            
            print(f"Chi-square statistic: {chi2:.4f}")
            print(f"p-value: {p_value:.4f}")
        else:
            # Use t-test for AOV
            control_purchases = results.loc['control', 'purchases']
            treatment_purchases = results.loc['treatment', 'purchases']
            control_aov = results.loc['control', 'aov']
            treatment_aov = results.loc['treatment', 'aov']
            
            t_statistic, p_value = stats.ttest_ind_from_stats(
                mean1=control_aov, std1=results.loc['control', 'total_spent']/np.sqrt(control_purchases), nobs1=control_purchases,
                mean2=treatment_aov, std2=results.loc['treatment', 'total_spent']/np.sqrt(treatment_purchases), nobs2=treatment_purchases
            )
            
            print(f"t-statistic: {t_statistic:.4f}")
            print(f"p-value: {p_value:.4f}")

# Analyze and visualize results
analyze_results(results)

# Visualize results
metrics = ['ctr', 'cr', 'aov']
fig, axs = plt.subplots(1, 3, figsize=(15, 5))

for i, metric in enumerate(metrics):
    control_value = results.loc['control', metric]
    treatment_value = results.loc['treatment', metric]
    
    axs[i].bar(['Control', 'Treatment'], [control_value, treatment_value])
    axs[i].set_title(f'{metric.upper()} Comparison')
    axs[i].set_ylabel(metric.upper())
    
    for j, v in enumerate([control_value, treatment_value]):
        axs[i].text(j, v, f'{v:.4f}', ha='center', va='bottom')

plt.tight_layout()
plt.show()