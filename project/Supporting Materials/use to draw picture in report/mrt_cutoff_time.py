import numpy as np
import matplotlib.pyplot as plt
from main import simulate, generate_service_time

def simulate_with_cutoff(seed, transient_time):
    np.random.seed(seed)

    n = 8
    h = 3
    time_end = 2000.0
    lambda_ = 1.6
    a2l, a2u = 0.9, 1.1
    p_k = [0.22, 0.28, 0.3, 0.08, 0.07, 0.05]
    mu, alpha = 0.8, 0.8
    J = len(p_k)

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
            job_id = i + 1
            subjob_id = j + 1
            service_time = generate_service_time(mu, alpha)
            sub_jobs.append((job_id, subjob_id, service_time))
        jobs.append({
            'arrival_time': arrival_times[i],
            'sub_jobs': sub_jobs,
            'num_sub_jobs': k
        })

    _, dep_events = simulate(n, h, time_end, 'random', arrival_times, jobs)

    response_times = []
    for arrival, departure in dep_events:
        if departure >= transient_time:
            response_times.append(departure - arrival)

    if len(response_times) > 0:
        return np.mean(response_times)
    else:
        return np.nan

cutoff_values = [100, 200, 400, 600, 800,1000,1200]
mrt_results = []

for cutoff in cutoff_values:
    mrt_list = []
    for seed in range(5):
        mrt = simulate_with_cutoff(seed, cutoff)
        mrt_list.append(mrt)
    avg_mrt = np.mean(mrt_list)
    mrt_results.append(avg_mrt)
    print(f"Cutoff={cutoff}, MRT={avg_mrt:.4f}")

plt.figure(figsize=(8, 5))
plt.plot(cutoff_values, mrt_results, marker='o')
plt.xlabel("Transient Cutoff Time")
plt.ylabel("Mean Response Time (MRT)")
plt.title("Sensitivity of MRT to Transient Cutoff Time")
plt.grid(True)
plt.tight_layout()
plt.savefig("mrt_and_transient_cutoff time.png")
plt.show()