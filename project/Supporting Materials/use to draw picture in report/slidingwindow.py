import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import stats

def simulate(seed, output_dir='output'):
    np.random.seed(seed)
    λ, a2l, a2u = 1.6, 0.9, 1.1
    mu, alpha = 0.8, 0.8
    num_servers, h = 8, 3
    time_end = 2000
    current_time = 0
    arrival_times = []

    while current_time < time_end:
        interarrival = np.random.exponential(1 / λ) * np.random.uniform(a2l, a2u)
        current_time += interarrival
        if current_time < time_end:
            arrival_times.append(current_time)

    jobs = []
    for i, arrival in enumerate(arrival_times):
        k = np.random.choice([1,2,3,4,5,6], p=[0.22,0.28,0.3,0.08,0.07,0.05])
        sub_jobs = [(i + 1, j + 1, (1/mu)*(-np.log(1 - np.random.uniform()))**(1/alpha)) for j in range(k)]
        jobs.append({
            'arrival_time': arrival,
            'sub_jobs': sub_jobs,
            'num_sub_jobs': k
        })

    server_status = ['empty'] * num_servers
    server_end_time = [float('inf')] * num_servers
    server_subjob = [None] * num_servers
    server_start_time = [None] * num_servers
    high_queue, low_queue = [], []
    job_index = 0
    current_time = 0
    dep_events = []

    while (job_index < len(jobs) or high_queue or low_queue or any(s == 'busy' for s in server_status)) and current_time < time_end:
        next_arrival = jobs[job_index]['arrival_time'] if job_index < len(jobs) else float('inf')
        busy_departures = [et for status, et in zip(server_status, server_end_time) if status == 'busy']
        next_departure = min(busy_departures) if busy_departures else float('inf')
        next_event_time = min(next_arrival, next_departure)

        if next_event_time >= time_end:
            break

        current_time = next_event_time

        if current_time == next_arrival:
            job = jobs[job_index]
            free_servers = [i for i, s in enumerate(server_status) if s == 'empty']
            for subjob in job['sub_jobs']:
                job_id, sub_id, service_time = subjob
                if free_servers:
                    sid = free_servers.pop(0)
                    server_status[sid] = 'busy'
                    server_end_time[sid] = current_time + service_time
                    server_subjob[sid] = (job_id, sub_id)
                    server_start_time[sid] = job['arrival_time']
                    dep_events.append((job['arrival_time'], current_time + service_time))
                else:
                    (high_queue if job['num_sub_jobs'] <= h else low_queue).append((subjob, job['arrival_time']))
            job_index += 1

        for sid in range(num_servers):
            if server_status[sid] == 'busy' and server_end_time[sid] == current_time:
                server_status[sid] = 'empty'
                if high_queue:
                    subjob, arrival = high_queue.pop(0)
                elif low_queue:
                    subjob, arrival = low_queue.pop(0)
                else:
                    continue
                job_id, sub_id, service_time = subjob
                server_status[sid] = 'busy'
                server_end_time[sid] = current_time + service_time
                server_subjob[sid] = (job_id, sub_id)
                server_start_time[sid] = arrival
                dep_events.append((arrival, current_time + service_time))

    dep_events.sort(key=lambda x: x[0])
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"dep_5_{seed - 9}.txt")
    with open(filename, 'w') as f:
        for a, d in dep_events:
            f.write(f"{a:.4f} {d:.4f}\n")
    print(f"Saved: {filename}")

for s in range(1, 21):
    simulate(seed=s+9)

response_matrix = []
for s in range(1, 21):
    with open(f"output/dep_5_{s}.txt", 'r') as f:
        lines = f.readlines()
        responses = [float(d) - float(a) for a, d in (line.split() for line in lines)]
        response_matrix.append(responses)

min_len = min(len(r) for r in response_matrix)
response_matrix = [r[:min_len] for r in response_matrix]
mean_response = np.mean(response_matrix, axis=0)

def smooth(data, w):
    return np.convolve(data, np.ones(2*w+1)/(2*w+1), mode='valid')

plt.figure(figsize=(10,6))
plt.plot(range(len(mean_response)), mean_response, label="Unsmoothed", alpha=0.5, color='gray')
plt.axvline(x=3361, color='red', linestyle='--', label='Cutoff at 800s (Subjob Index 3361)')
for w in [200, 400, 600]:
    smoothed = smooth(mean_response, w)
    plt.plot(range(w, w+len(smoothed)), smoothed, label=f"W = {w}")
plt.xlabel("Subjob Index")
plt.ylabel("Mean Response Time")
plt.title("Smoothed Mean Response Time Across 20 Replications")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("smoothed_response_time.png")
plt.show()

cumulative_mean = np.cumsum(mean_response) / np.arange(1, len(mean_response) + 1)
plt.figure(figsize=(10,6))
plt.plot(range(len(cumulative_mean)), cumulative_mean, label="Cumulative Mean")
plt.axvline(x=3361, color='red', linestyle='--', label='Cutoff at 800s (Subjob Index 3361)')
plt.xlabel("Subjob Index")
plt.ylabel("Cumulative Mean Response Time")
plt.title("Cumulative Mean Response Time Across 20 Replications")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("cumulative_mean_response_time.png")
plt.show()

steady_state_mrts = []
for responses in response_matrix:
    steady_state_responses = responses[3361:]
    steady_state_mrts.append(np.mean(steady_state_responses))

mean_mrt = np.mean(steady_state_mrts)
std_mrt = np.std(steady_state_mrts, ddof=1)
n = len(steady_state_mrts)
alpha = 0.05
mf = stats.t.ppf(1-alpha/2, n-1) / np.sqrt(n)
confidence_interval = mean_mrt + np.array([-1,1]) * mf * std_mrt
print(f"Stable MRT: {mean_mrt:.4f}")
print(f"Confidence Interval: [{confidence_interval[0]:.4f}, {confidence_interval[1]:.4f}]")