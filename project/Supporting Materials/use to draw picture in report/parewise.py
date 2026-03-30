#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import numpy as np
import os
import pandas as pd
from scipy.stats import ttest_rel

def generate_service_time(mu, alpha):
    u = np.random.uniform(0, 1)
    service_time = (1 / mu) * (-np.log(1 - u)) ** (1 / alpha)
    return service_time

def simulate(num_servers, h, time_end, mode, jobs):
    server_status = ['empty'] * num_servers
    server_end_time = [float('inf')] * num_servers
    server_subjob = [None] * num_servers
    server_start_time = [None] * num_servers

    high_queue = []
    low_queue = []

    current_time = 0
    job_index = 0
    completion_record = {}

    dep_events = []

    while (job_index < len(jobs) or high_queue or low_queue or any(s == 'busy' for s in server_status)) and current_time < time_end:
        if job_index < len(jobs):
            next_arrival = jobs[job_index]['arrival_time']
        else:
            next_arrival = float('inf')
        busy_departures = [end_time for status, end_time in zip(server_status, server_end_time) if status == 'busy']
        next_departure = min(busy_departures) if busy_departures else float('inf')
        next_event_time = min(next_arrival, next_departure)

        if next_event_time >= time_end:
            break

        current_time = next_event_time

        if current_time == next_arrival:
            job = jobs[job_index]
            free_servers = [i for i, status in enumerate(server_status) if status == 'empty']
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
                    if job['num_sub_jobs'] <= h:
                        high_queue.append((subjob, job['arrival_time']))
                    else:
                        low_queue.append((subjob, job['arrival_time']))
            job_index += 1

        for sid in range(num_servers):
            if server_status[sid] == 'busy' and server_end_time[sid] == current_time:
                job_id, sub_id = server_subjob[sid]
                completion_record.setdefault(job_id, []).append(current_time)

                server_status[sid] = 'empty'
                server_end_time[sid] = float('inf')
                server_subjob[sid] = None
                server_start_time[sid] = None

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

    response_times = []
    TRANSIENT_TIME = 1000
    for job_id in range(1, len(jobs) + 1):
        if job_id in completion_record and len(completion_record[job_id]) == jobs[job_id - 1]['num_sub_jobs']:
            finish = max(completion_record[job_id])
            if mode == 'random':
                if finish >= TRANSIENT_TIME:
                    rt = finish - jobs[job_id - 1]['arrival_time']
                    response_times.append(rt)
            else:
                rt = finish - jobs[job_id - 1]['arrival_time']
                response_times.append(rt)

    mrt = sum(response_times) / len(response_times) if response_times else 0
    dep_events.sort(key=lambda x: x[1])

    return mrt, dep_events

def main(t):
    config_dir = 'config'
    output_dir = 'output'
    mode_path = os.path.join(config_dir, f"mode_{t}.txt")
    para_path = os.path.join(config_dir, f"para_{t}.txt")
    arrival_path = os.path.join(config_dir, f"interarrival_{t}.txt")
    service_path = os.path.join(config_dir, f"service_{t}.txt")

    with open(mode_path, 'r') as f:
        mode = f.read().strip()

    with open(para_path, 'r') as f:
        lines = f.readlines()
        num_servers = int(lines[0])
        threshold = int(lines[1])
        if mode == 'random':
            time_end = float(lines[2])
            np.random.seed(int(t))
        else:
            time_end = float('inf')

    jobs = []

    if mode == 'trace':
        between_arrival = np.loadtxt(arrival_path)
        arrival_times = []
        current_time = 0
        for gap in between_arrival:
            current_time += gap
            arrival_times.append(current_time)

        service_data = np.loadtxt(service_path)
        for i in range(len(service_data)):
            sub_jobs = []
            for j in range(len(service_data[i])):
                if not np.isnan(service_data[i][j]):
                    sub_jobs.append((i + 1, j + 1, service_data[i][j]))
            jobs.append({
                'arrival_time': arrival_times[i],
                'sub_jobs': sub_jobs,
                'num_sub_jobs': len(sub_jobs)
            })

        mrt, events = simulate(num_servers, threshold, time_end, mode, jobs)

    else:
        with open(arrival_path, 'r') as f:
            line1 = list(map(float, f.readline().split()))
            λ, a2l, a2u = line1
            subjob_distribution = list(map(float, f.readline().split()))
            max_subjob = len(subjob_distribution)

        with open(service_path, 'r') as f:
            mu, alpha = map(float, f.read().split())

        seeds = range(10)
        mrt_h2, mrt_h3, mrt_h4, mrt_h5 = [], [], [], []

        for seed in seeds:
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
                k = np.random.choice(range(1, max_subjob + 1), p=subjob_distribution)
                sub_jobs = []
                for j in range(k):
                    service_time = generate_service_time(mu, alpha)
                    sub_jobs.append((i + 1, j + 1, service_time))
                jobs.append({
                    'arrival_time': arrival_times[i],
                    'sub_jobs': sub_jobs,
                    'num_sub_jobs': k
                })

            mrt_2, _ = simulate(num_servers, h=2, time_end=time_end, mode=mode, jobs=jobs)
            mrt_3, _ = simulate(num_servers, h=3, time_end=time_end, mode=mode, jobs=jobs)
            mrt_4, _ = simulate(num_servers, h=4, time_end=time_end, mode=mode, jobs=jobs)
            mrt_5, _ = simulate(num_servers, h=5, time_end=time_end, mode=mode, jobs=jobs)

            mrt_h2.append(mrt_2)
            mrt_h3.append(mrt_3)
            mrt_h4.append(mrt_4)
            mrt_h5.append(mrt_5)

        data = pd.DataFrame({
            'MRT': np.concatenate([mrt_h2, mrt_h3, mrt_h4, mrt_h5]),
            'Group': ['h=2']*len(seeds) + ['h=3']*len(seeds) + ['h=4']*len(seeds) + ['h=5']*len(seeds)
        })

        pairs = [
            ('h=2', 'h=3'), ('h=2', 'h=4'), ('h=2', 'h=5'),
            ('h=3', 'h=4'), ('h=3', 'h=5'), ('h=4', 'h=5')
        ]

        results = []
        mrt_dict = {'h=2': mrt_h2, 'h=3': mrt_h3, 'h=4': mrt_h4, 'h=5': mrt_h5}
        for group1, group2 in pairs:
            group1_data = mrt_dict[group1]
            group2_data = mrt_dict[group2]
            stat, p_val = ttest_rel(group1_data, group2_data)
            significant = 'Notable Difference' if p_val < 0.05 else 'Able Difference'
            results.append({
                'Comparison': f'{group1} and {group2}',
                'p-value': p_val,
                'Significance': significant
            })

        print("Pairwise T-Test Results (α = 0.05):")
        print("| Comparison   | p-value    | Result                 |")
        print("|--------------|------------|------------------------|")
        for result in results:
            print(f"{result['Comparison']} | {result['p-value']:.10f} | {result['Significance']}")
        print(f"Average MRT for h=2: {np.mean(mrt_h2):.4f}")
        print(f"Average MRT for h=3: {np.mean(mrt_h3):.4f}")
        print(f"Average MRT for h=4: {np.mean(mrt_h4):.4f}")
        print(f"Average MRT for h=5: {np.mean(mrt_h5):.4f}")

if __name__ == "__main__":
    main(sys.argv[1])