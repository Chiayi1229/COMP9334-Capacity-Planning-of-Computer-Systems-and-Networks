import numpy as np
import matplotlib.pyplot as plt

n = 8
h = 3
time_end = 2000
lambda_, a2l, a2u = 1.6, 0.9, 1.1
mu, alpha = 0.8, 0.8

np.random.seed(42)
arrival_times = []
current_time = 0
while current_time < time_end:
    interarrival = np.random.exponential(1 / lambda_) * np.random.uniform(a2l, a2u)
    current_time += interarrival
    if current_time < time_end:
        arrival_times.append(current_time)

jobs = []
for i in range(len(arrival_times)):
    k = np.random.choice([1, 2, 3, 4, 5, 6], p=[0.22, 0.28, 0.3, 0.08, 0.07, 0.05])
    sub_jobs = []
    for j in range(k):
        service_time = (1 / mu) * (-np.log(1 - np.random.uniform())) ** (1 / alpha)
        sub_jobs.append((i + 1, j + 1, service_time))
    jobs.append({
        'arrival_time': arrival_times[i],
        'sub_jobs': sub_jobs,
        'num_sub_jobs': k
    })

def simulate(num_servers, h, time_end, jobs):
    server_status = ['empty'] * num_servers
    server_end_time = [float('inf')] * num_servers
    server_subjob = [None] * num_servers
    high_queue, low_queue = [], []
    current_time, job_index = 0, 0
    completion_record = {}
    dep_events = []

    while (job_index < len(jobs) or high_queue or low_queue or any(s == 'busy' for s in server_status)) and current_time < time_end:
        if job_index < len(jobs):
            next_arrival = jobs[job_index]['arrival_time']
        else:
            next_arrival = float('inf')
        busy_departures = [et for s, et in zip(server_status, server_end_time) if s == 'busy']
        next_departure = min(busy_departures) if busy_departures else float('inf')
        current_time = min(next_arrival, next_departure)
        if current_time >= time_end:
            break

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
                    dep_events.append((job['arrival_time'], current_time + service_time))
                else:
                    if job['num_sub_jobs'] <= h:
                        high_queue.append((subjob, job['arrival_time']))
                    else:
                        low_queue.append((subjob, job['arrival_time']))
            job_index += 1
        else:
            for sid in range(num_servers):
                if server_status[sid] == 'busy' and server_end_time[sid] == current_time:
                    job_id, sub_id = server_subjob[sid]
                    completion_record.setdefault(job_id, []).append(current_time)
                    server_status[sid] = 'empty'
                    server_end_time[sid] = float('inf')
                    server_subjob[sid] = None
                    if high_queue:
                        subjob, arr = high_queue.pop(0)
                    elif low_queue:
                        subjob, arr = low_queue.pop(0)
                    else:
                        continue
                    job_id, sub_id, service_time = subjob
                    server_status[sid] = 'busy'
                    server_end_time[sid] = current_time + service_time
                    server_subjob[sid] = (job_id, sub_id)
                    dep_events.append((arr, current_time + service_time))

    dep_events.sort(key=lambda x: x[1])
    return dep_events

events = simulate(n, h, time_end, jobs)
response_times = [d - a for a, d in events]
cumulative_mrt = np.cumsum(response_times) / np.arange(1, len(response_times) + 1)

cutoff_job_id = 800
plt.figure(figsize=(10, 5))
plt.plot(cumulative_mrt, label='Mean Response Time', color='purple')
plt.axvline(x=cutoff_job_id, color='red', linestyle='--', label=f'Job ID = {cutoff_job_id}')
plt.xlabel("Job ID")
plt.ylabel("Mean Response Time")
plt.title("Convergence of MRT (h=3)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("mrt_convergence_h3.png")
plt.show()