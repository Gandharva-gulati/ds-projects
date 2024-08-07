import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from datetime import datetime, timedelta

np.random.seed(42)

class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.clicks = 0
        self.purchases = 0
        self.total_spent = 0

class ABTest:
    def __init__(self, start_date, duration_days, total_users):
        self.start_date = start_date
        self.end_date = start_date + timedelta(days=duration_days)
        self.total_users = total_users
        self.users = [User(i) for i in range(total_users)]
        
        # Control group parameters
        self.control_ctr = 0.05
        self.control_cr = 0.02
        self.control_aov_mean = 50
        self.control_aov_std = 20
        
        # Treatment group parameters (slight improvements)
        self.treatment_ctr = 0.06
        self.treatment_cr = 0.025
        self.treatment_aov_mean = 55
        self.treatment_aov_std = 22
        
        # Assign users to groups
        self.control_users = self.users[:len(self.users)//2]
        self.treatment_users = self.users[len(self.users)//2:]
    
    def simulate_day(self, day):
        for user in self.users:
            if np.random.random() < 0.1:  # 10% chance user visits site on any given day
                if user in self.control_users:
                    self.simulate_user_journey(user, 'control')
                else:
                    self.simulate_user_journey(user, 'treatment')
    
    def simulate_user_journey(self, user, group):
        if group == 'control':
            ctr, cr, aov_mean, aov_std = self.control_ctr, self.control_cr, self.control_aov_mean, self.control_aov_std
        else:
            ctr, cr, aov_mean, aov_std = self.treatment_ctr, self.treatment_cr, self.treatment_aov_mean, self.treatment_aov_std
        
        # Simulate click on recommended product
        if np.random.random() < ctr:
            user.clicks += 1
            
            # Simulate purchase
            if np.random.random() < cr:
                user.purchases += 1
                order_value = max(0, np.random.normal(aov_mean, aov_std))
                user.total_spent += order_value
    
    def run_simulation(self):
        current_date = self.start_date
        while current_date <= self.end_date:
            self.simulate_day(current_date)
            current_date += timedelta(days=1)
    
    def get_results(self):
        control_clicks = sum(user.clicks for user in self.control_users)
        control_purchases = sum(user.purchases for user in self.control_users)
        control_revenue = sum(user.total_spent for user in self.control_users)
        
        treatment_clicks = sum(user.clicks for user in self.treatment_users)
        treatment_purchases = sum(user.purchases for user in self.treatment_users)
        treatment_revenue = sum(user.total_spent for user in self.treatment_users)
        
        results = {
            'control': {
                'users': len(self.control_users),
                'clicks': control_clicks,
                'purchases': control_purchases,
                'revenue': control_revenue,
                'ctr': control_clicks / len(self.control_users),
                'cr': control_purchases / control_clicks if control_clicks > 0 else 0,
                'aov': control_revenue / control_purchases if control_purchases > 0 else 0
            },
            'treatment': {
                'users': len(self.treatment_users),
                'clicks': treatment_clicks,
                'purchases': treatment_purchases,
                'revenue': treatment_revenue,
                'ctr': treatment_clicks / len(self.treatment_users),
                'cr': treatment_purchases / treatment_clicks if treatment_clicks > 0 else 0,
                'aov': treatment_revenue / treatment_purchases if treatment_purchases > 0 else 0
            }
        }
        return results

def analyze_results(results):
    for metric in ['ctr', 'cr', 'aov']:
        control_value = results['control'][metric]
        treatment_value = results['treatment'][metric]
        relative_improvement = (treatment_value - control_value) / control_value
        
        print(f"\n{metric.upper()} Analysis:")
        print(f"Control: {control_value:.4f}")
        print(f"Treatment: {treatment_value:.4f}")
        print(f"Relative Improvement: {relative_improvement:.2%}")
        
        # Perform statistical test
        if metric in ['ctr', 'cr']:
            # Use Chi-square test for rates
            control_successes = results['control']['clicks' if metric == 'ctr' else 'purchases']
            control_trials = results['control']['users' if metric == 'ctr' else 'clicks']
            treatment_successes = results['treatment']['clicks' if metric == 'ctr' else 'purchases']
            treatment_trials = results['treatment']['users' if metric == 'ctr' else 'clicks']
            
            chi2, p_value = stats.chi2_contingency([
                [control_successes, control_trials - control_successes],
                [treatment_successes, treatment_trials - treatment_successes]
            ])[:2]
            
            print(f"Chi-square statistic: {chi2:.4f}")
            print(f"p-value: {p_value:.4f}")
        else:
            # Use t-test for AOV
            control_purchases = results['control']['purchases']
            treatment_purchases = results['treatment']['purchases']
            control_aov = results['control']['aov']
            treatment_aov = results['treatment']['aov']
            
            t_statistic, p_value = stats.ttest_ind_from_stats(
                mean1=control_aov, std1=results['control']['revenue']/np.sqrt(control_purchases), nobs1=control_purchases,
                mean2=treatment_aov, std2=results['treatment']['revenue']/np.sqrt(treatment_purchases), nobs2=treatment_purchases
            )
            
            print(f"t-statistic: {t_statistic:.4f}")
            print(f"p-value: {p_value:.4f}")

# Run the simulation
start_date = datetime(2023, 1, 1)
duration_days = 30
total_users = 100000

ab_test = ABTest(start_date, duration_days, total_users)
ab_test.run_simulation()
results = ab_test.get_results()

# Analyze and visualize results
analyze_results(results)

# Visualize results
metrics = ['ctr', 'cr', 'aov']
fig, axs = plt.subplots(1, 3, figsize=(15, 5))

for i, metric in enumerate(metrics):
    control_value = results['control'][metric]
    treatment_value = results['treatment'][metric]
    
    axs[i].bar(['Control', 'Treatment'], [control_value, treatment_value])
    axs[i].set_title(f'{metric.upper()} Comparison')
    axs[i].set_ylabel(metric.upper())
    
    for j, v in enumerate([control_value, treatment_value]):
        axs[i].text(j, v, f'{v:.4f}', ha='center', va='bottom')

plt.tight_layout()
plt.show()