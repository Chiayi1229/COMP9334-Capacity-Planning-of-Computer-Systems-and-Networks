import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from main import simulate, generate_service_time

n = 8
h = 3
lambda_ = 1.6
a2l, a2u = 0.9, 1.1
p_k = [0.22, 0.28, 0.3, 0.08, 0.07, 0.05]
mu, alpha = 0.8, 0.8
J = len(p_k)
mode = "random"


time_ends = list(range(2000, 15000, 1000))
mrt_means = []
mrt_ci_lower = []
mrt_ci_upper = []

for time_end in time_ends:
    mrts = []
    for seed in range(50):
        np.random.seed(seed)
        arrival_times = []
        current_time = 0
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
                job_id = i+1
                subjob_id = j+1
                service_time = generate_service_time()
                sub_jobs.append((job_id, subjob_id, service_time))
            jobs.append({
                'arrival_time': arrival_times[i],
                'sub_jobs': sub_jobs,
                'num_sub_jobs': k
            })

        mrt = simulate(n, h, time_end, mode, arrival_times, jobs)[0]
        if mrt > 0:
            mrts.append(mrt)

    if len(mrts) >= 10:
        mean_mrt = np.mean(mrts)
        std_mrt = np.std(mrts, ddof=1)
        if std_mrt > 0:
            ci = stats.t.interval(confidence=0.95, df=len(mrts)-1, loc=mean_mrt, scale=std_mrt/np.sqrt(len(mrts)))
            mrt_means.append(mean_mrt)
            mrt_ci_lower.append(ci[0])
            mrt_ci_upper.append(ci[1])
        else:
            mrt_means.append(mean_mrt)
            mrt_ci_lower.append(mean_mrt)
            mrt_ci_upper.append(mean_mrt)
    else:
        mrt_means.append(np.nan)
        mrt_ci_lower.append(np.nan)
        mrt_ci_upper.append(np.nan)

valid_indices = ~np.isnan(mrt_means)
time_ends_plot = np.array(time_ends)[valid_indices]
mrt_means_plot = np.array(mrt_means)[valid_indices]
mrt_ci_lower_plot = np.array(mrt_ci_lower)[valid_indices]
mrt_ci_upper_plot = np.array(mrt_ci_upper)[valid_indices]

window_size = 3
mrt_means_smoothed = np.convolve(mrt_means_plot, np.ones(window_size)/window_size, mode='valid')
time_ends_smoothed = time_ends_plot[(window_size-1)//2:-(window_size-1)//2]

plt.figure()
plt.plot(time_ends_plot, mrt_means_plot, marker='o', color='blue', label='Mean MRT', alpha=0.5)
plt.plot(time_ends_smoothed, mrt_means_smoothed, color='red', label=f'Moving Average (window={window_size})')
plt.fill_between(time_ends_plot, mrt_ci_lower_plot, mrt_ci_upper_plot, color='blue', alpha=0.2, label='95% Confidence Interval')
plt.title(f"MRT vs Simulation Duration (h={h})")
plt.xlabel("Simulation Duration (time_end)")
plt.ylabel("Average MRT")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("mrt_vs_simulation_duration.png")
plt.close()

print("MRT annlyse")
for i in range(1, len(mrt_means_smoothed)):
    diff = abs(mrt_means_smoothed[i] - mrt_means_smoothed[i-1])
    print(f"time_end {time_ends_smoothed[i-1]} to {time_ends_smoothed[i]} MRT change: {diff:.4f}")
    if diff < 0.01:
        print(f"suggest time_end = {time_ends_smoothed[i]},MRT change lower than 0.01,system is stable")
        break