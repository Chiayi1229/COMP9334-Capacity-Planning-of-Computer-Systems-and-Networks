import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from main import simulate

num_servers = 8
time_end = 18000
replications = 60
h_list = [1, 2, 3, 4, 5, 6]

λ = 1.6
a2l, a2u = 0.9, 1.1
mu, alpha = 0.8, 0.8
p_k = [0.22, 0.28, 0.30, 0.08, 0.07, 0.05]
max_k = len(p_k)

def generate_service_time(mu, alpha):
    u = np.random.uniform(0, 1)
    service_time = (1 / mu) * (-np.log(1 - u)) ** (1 / alpha)
    return service_time



mean_mrts = []
ci_lowers = []
ci_uppers = []

for h in h_list:
    mrt_samples = []
    for seed in range(replications):
        np.random.seed(seed)
        arrival_times = []
        current_time = 0
        while current_time < time_end:
            interval = np.random.exponential(1 / λ) * np.random.uniform(a2l, a2u)
            current_time += interval
            if current_time < time_end:
                arrival_times.append(current_time)

        jobs = []
        for i in range(len(arrival_times)):
            k = np.random.choice(range(1, max_k + 1), p=p_k)
            sub_jobs = []
            for j in range(k):
                st = generate_service_time(mu, alpha)
                sub_jobs.append((i + 1, j + 1, st))
            jobs.append({'arrival_time': arrival_times[i], 'sub_jobs': sub_jobs, 'num_sub_jobs': k})

        mrt, _ = simulate(num_servers, h, time_end, 'random', arrival_times, jobs)
        mrt_samples.append(mrt)

    mean = np.mean(mrt_samples)
    std_err = stats.sem(mrt_samples)
    ci = stats.t.interval(0.95, df=replications-1, loc=mean, scale=std_err)
    mean_mrts.append(mean)
    ci_lowers.append(mean - ci[0])
    ci_uppers.append(ci[1] - mean)

plt.figure(figsize=(10, 6))
plt.errorbar(h_list, mean_mrts, yerr=[ci_lowers, ci_uppers], fmt='-o', capsize=5, label='MRT ± 95% CI')
plt.xlabel("Threshold h")
plt.ylabel("Mean Response Time")
plt.title("MRT vs Threshold h with 95% Confidence Intervals")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("mrt_vs_h_CI.png")
plt.show()