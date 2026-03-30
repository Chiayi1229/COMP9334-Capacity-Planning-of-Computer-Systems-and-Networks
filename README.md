# COMP9334-Capacity-Planning-of-Computer-Systems-and-Networks

Project Overview

This project implements and analyses a priority queueing simulation for server farms with batch arrivals.
The goal is to evaluate system performance using simulation techniques and determine optimal system parameters such as simulation length, transient cutoff time, and threshold 
ℎ
h.

The project includes:

Simulation validation
Random generator verification
Reproducibility analysis
Stability testing
Parameter optimisation
Q1: Simulation Validation
Q1(a) Program Testing

The simulation program was tested on the CSE lab machine and successfully passed all provided test cases:

Test 1 – Test 7

This confirms the correctness of the implementation.

Q1(b) Random Mode Verification

To verify that the simulation correctly follows the theoretical distributions, several experiments were conducted.

Two scripts were used:

sub-job.py
servicetime.py

These scripts generate large numbers of samples and compare them with theoretical distributions.

The following random variables were verified:

1. Inter-arrival Time

Arrival time follows:

Interarrival = Exponential(λ = 1.6) × Uniform(0.9, 1.1)

The simulation results closely match the theoretical distribution, confirming correctness.

2. Number of Sub-jobs

The number of sub-jobs was generated using probability vectors defined in the tests:

Example probabilities:
Test5:
0.400 0.300 0.200 0.050 0.050

Test6:
0.300 0.300 0.200 0.100 0.050 0.050

Test7:
0.300 0.250 0.200 0.150 0.050 0.050

The experimental frequencies match the theoretical probabilities.

3. Service Time Distribution

Service time follows a Weibull distribution:

S(t) = 1 − exp(−(μt)^α)

Parameters used:
μ = 0.8
α = 0.8

Using Inverse Transform Sampling:

t = (1 / μ) · (−ln(1 − u))^(1 / α)

Simulation results match the theoretical CDF and histogram distribution, confirming correctness.

Q2: Reproducibility of Simulation

To ensure reproducibility, simulations were executed using fixed random seeds.

Method:

np.random.seed(seed)

Experiment setup:

Seeds tested: 0 – 39
Each seed repeated: 5 simulations
Metric analysed: Mean Response Time (MRT)

Results show:

Consistent MRT trends
Stable distribution across different seeds
Good reproducibility of the simulation system.
Q3: Simulation Parameter Analysis
Q3(a) Determining Simulation Length, Replications, and Cutoff Time

Several scripts were used:

time_end_test.py
mrt_cutoff_time.py
slidingwindow.py

Simulation Length

Different simulation durations were tested.

Result:
After time_end = 8000, MRT becomes stable around:

MRT ≈ 3.15 – 3.16

Therefore:

Recommended simulation length:
time_end = 8000

Replications

Each configuration used:

5 replications

This provides stable results while keeping computational cost manageable.

Transient Cutoff Time

Analysis shows the system stabilises around:

cutoff = 800

This is supported by:

MRT sensitivity analysis
Sliding window analysis
Cumulative mean analysis
Q3(b) Optimal Threshold h

To determine the best value of h, simulations were conducted for:

h = 0 – 6

Each value was tested with:
60 independent simulations

Results:

h	Mean MRT
0	3.3479
1	3.2357
2	3.1729
3	3.1559 (Best)
4	3.2058
5	3.2817
6	3.3934

The best threshold is:

h = 3

This value provides:

Lowest MRT
Stable confidence interval

Pairwise t-tests confirmed the statistical significance of the differences.

Final Conclusion

From the simulation analysis:

Optimal parameters are:

Simulation length: 8000
Transient cutoff time: 800
Replications: 5
Best threshold: h = 3

These settings provide stable and reliable simulation results.

Reference

Simulation reference code:
https://github.com/co4524/M-M-m-SystemSimulation
