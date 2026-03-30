#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Based on code from: https://github.com/co4524/M-M-m-SystemSimulation/blob/master/R07944048_hw2.py
"""
import sys
import numpy as np

def generate_service_time(mu, alpha):
    u = np.random.uniform(0, 1)
    service_time = (1 / mu) * (-np.log(1 - u)) ** (1 / alpha)
    return service_time


def simulate(n, h, time_end, mode, arrival_times, jobs):
    high_queue = []
    low_queue = []
    servers = []
    for i in range(n):
        servers.append({'status': 'empty', 'departure_time': float('inf'), 'sub_job': None, 'arrival_time': None})

    completion_record = {}
    events = []

    current_time = 0
    job_index = 0

    while (job_index < len(jobs) or high_queue or low_queue or any(s['status'] == 'busy' for s in servers)) and current_time < time_end:
        if job_index < len(jobs):
            next_arrival = jobs[job_index]['arrival_time']
        else:
            next_arrival = float('inf')

        next_departure = float('inf')
        for s in servers:
            if s['status'] == 'busy' and s['departure_time'] < next_departure:
                next_departure = s['departure_time']

        current_time = min(next_arrival, next_departure)

        if current_time >= time_end:
            break

        if current_time == next_arrival:
            job = jobs[job_index]
            idle_servers = []
            for i in range(n):
                if servers[i]['status'] == 'empty':
                    idle_servers.append(i)
            for sub_job in job['sub_jobs']:
                job_id, sub_id, service_time = sub_job
                if idle_servers:
                    sid = idle_servers.pop(0)
                    servers[sid]['status'] = 'busy'
                    servers[sid]['departure_time'] = current_time + service_time
                    servers[sid]['sub_job'] = (job_id, sub_id)
                    servers[sid]['arrival_time'] = job['arrival_time']
                    events.append((job['arrival_time'], current_time + service_time))
                else:
                    if job['num_sub_jobs'] <= h:
                        high_queue.append([sub_job, job['arrival_time']])
                    else:
                        low_queue.append([sub_job, job['arrival_time']])
            job_index += 1

        else:
            for i in range(n):
                if servers[i]['status'] == 'busy' and servers[i]['departure_time'] == current_time:
                    job_id, sub_id = servers[i]['sub_job']
                    if job_id not in completion_record:
                        completion_record[job_id] = []
                    completion_record[job_id].append(current_time)

                    servers[i]['status'] = 'empty'
                    servers[i]['departure_time'] = float('inf')
                    servers[i]['sub_job'] = None
                    servers[i]['arrival_time'] = None

                    if high_queue:
                        sub_job, arrival = high_queue.pop(0)
                        job_id, sub_id, service_time = sub_job
                        servers[i]['status'] = 'busy'
                        servers[i]['departure_time'] = current_time + service_time
                        servers[i]['sub_job'] = (job_id, sub_id)
                        servers[i]['arrival_time'] = arrival
                        events.append((arrival, current_time + service_time))
                    elif low_queue:
                        sub_job, arrival = low_queue.pop(0)
                        job_id, sub_id, service_time = sub_job
                        servers[i]['status'] = 'busy'
                        servers[i]['departure_time'] = current_time + service_time
                        servers[i]['sub_job'] = (job_id, sub_id)
                        servers[i]['arrival_time'] = arrival
                        events.append((arrival, current_time + service_time))

    response_times = []
    TRANSIENT_TIME = 200
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
    if len(response_times) > 0:
        mrt = sum(response_times) / len(response_times)
    else:
        mrt = 0
    events.sort(key=lambda x: x[1])
    return mrt, events

def main(t):
    config_folder = 'config'
    out_folder = 'output'

    mode_file = f"{config_folder}/mode_{t}.txt"
    para_file = f"{config_folder}/para_{t}.txt"
    interarrival_file = f"{config_folder}/interarrival_{t}.txt"
    service_file = f"{config_folder}/service_{t}.txt"

    with open(mode_file, 'r') as f:
        mode = f.read().strip()

    with open(para_file, 'r') as f:
        lines = f.readlines()
        n = int(lines[0])
        h = int(lines[1])
        if mode == 'random':
            time_end = float(lines[2])
        else:
            time_end = float('inf')

    if mode == 'trace':
        between_times = np.loadtxt(interarrival_file)
        arrival_times = [between_times[0]]
        for i in range(1, len(between_times)):
            arrival_times.append(arrival_times[-1] + between_times[i])
        service_data = np.loadtxt(service_file)
        jobs = []
        for i in range(len(service_data)):
            sub_jobs = []
            for j in range(len(service_data[i])):
                if not np.isnan(service_data[i][j]):
                    sub_jobs.append((i + 1, j + 1, service_data[i][j]))
            jobs.append({'arrival_time': arrival_times[i], 'sub_jobs': sub_jobs, 'num_sub_jobs': len(sub_jobs)})
        mrt, events = simulate(n, h, time_end, mode, arrival_times, jobs)

    else:
        with open(interarrival_file, 'r') as f:
            lines = f.readlines()
            lambda_, a2l, a2u = map(float, lines[0].split())
            p_k = list(map(float, lines[1].split()))
            max_subjob = len(p_k)
        with open(service_file, 'r') as f:
            mu, alpha = map(float, f.read().split())

        num_replications = 5
        mrt_list = []
        all_events = []
        for seed in range(num_replications):
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
                num_sub_jobs = np.random.choice(range(1, max_subjob + 1), p=p_k)
                sub_jobs = []
                for j in range(num_sub_jobs):
                    service_time = generate_service_time(mu, alpha)
                    sub_jobs.append((i + 1, j + 1, service_time))
                jobs.append({'arrival_time': arrival_times[i], 'sub_jobs': sub_jobs, 'num_sub_jobs': num_sub_jobs})
            mrt, events = simulate(n, h, time_end, mode, arrival_times, jobs)
            mrt_list.append(mrt)
            all_events.extend(events)
        mrt = sum(mrt_list) / len(mrt_list)
        events = all_events

    mrt_file = out_folder + '/mrt_' + str(t) + '.txt'
    dep_file = out_folder + '/dep_' + str(t) + '.txt'

    with open(mrt_file, 'w') as f:
        f.write(f"{mrt:.4f}")

    with open(dep_file, 'w') as f:
        for arrival, departure in events:
            if mode == 'random' and departure > time_end:
                continue
            f.write(f"{arrival:.4f} {departure:.4f}\n")

    print(f"Test {t} done. MRT = {mrt:.4f}")
    print(f"Saved to {mrt_file} and {dep_file}")

if __name__ == "__main__":
    main(sys.argv[1])