import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from main import simulate, generate_service_time

def simulate_mrt_given_seed(seed, h=3, time_end=2000.0, replications=5):
    np.random.seed(seed)
    lambda_, a2l, a2u = 1.6, 0.9, 1.1
    p_k = [0.22, 0.28, 0.3, 0.08, 0.07, 0.05]
    mu, alpha = 0.8, 0.8
    n = 8
    J = len(p_k)

    def one_run():
        arrival_times, current_time = [], 0
        while current_time < time_end:
            original_gap = np.random.exponential(1 / lambda_)
            random_factor = np.random.uniform(a2l, a2u)
            final_gap = original_gap * random_factor
            current_time += final_gap
            if current_time < time_end:
                arrival_times.append(current_time)

        jobs = []
        for i in range(len(arrival_times)):
            k = np.random.choice(range(1, J + 1), p=p_k)
            sub_jobs = []
            for j in range(k):
                job_id = i + 1
                subjob_id = j + 1
                service_time = generate_service_time()
                sub_jobs.append((job_id, subjob_id, service_time))
            jobs.append({'arrival_time': arrival_times[i], 'sub_jobs': sub_jobs, 'num_sub_jobs': k})
        return simulate(n, h, time_end, 'random', arrival_times, jobs)[0]

    results = []
    for i in range(replications):
        result = one_run()
        results.append(result)
    return results 


all_mrts = []
for seed in range(40):
    all_mrts.append(simulate_mrt_given_seed(seed, replications=5))

plt.figure(figsize=(10, 6))
sns.boxplot(data=all_mrts)
plt.xlabel("Seed")
plt.ylabel("Mean Response Time (MRT)")
plt.title("MRT per Seed (5 replications each)")
plt.tight_layout()
plt.savefig("mrt_per_seed_boxplot.png")
plt.show()
