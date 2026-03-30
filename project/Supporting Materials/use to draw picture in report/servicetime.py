import numpy as np
import matplotlib.pyplot as plt

def generate_service_time(mu, alpha):
    u = np.random.uniform(0, 1)
    service_time = (1 / mu) * (-np.log(1 - u)) ** (1 / alpha)
    return service_time

mu = 0.8
alpha = 0.8
sample_size = 100000

service_times = [generate_service_time(mu, alpha) for _ in range(sample_size)]
service_times = np.array(service_times)

sorted_times = np.sort(service_times)
cdf = np.arange(1, sample_size + 1) / sample_size
theory_cdf = 1 - np.exp(-(mu * sorted_times) ** alpha)

plt.figure(figsize=(10,6))
plt.plot(sorted_times, cdf, label='Empirical CDF', color='blue')
plt.plot(sorted_times, theory_cdf, label='Theoretical CDF: $S(t)=1-e^{-(\\mu t)^\\alpha}$', color='red', linestyle='--')
plt.xlabel("Service Time")
plt.ylabel("CDF")
plt.title("Empirical vs Theoretical CDF of Service Time")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("service_time_cdf_verification.png")
plt.show()