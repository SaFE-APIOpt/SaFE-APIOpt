import numpy as np
import timeit
import psutil
import pandas as pd
import os

output_file = "output_.xlsx"

# Define the two APIs to compare
api1 = "numpy.prod"
api2 = "numpy.multiply.reduce"
package = "numpy"
description = "Computes the product of array elements using two different methods."

def get_memory_usage():
    """
    Return the current process's memory usage in megabytes.
    """
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 ** 2

def method_v1(A):
    """
    Compute row-wise product using numpy.prod.
    """
    return np.prod(A, axis=1)

def method_v2(A):
    """
    Compute row-wise product using numpy.multiply.reduce.
    """
    return np.multiply.reduce(A, axis=1)

def benchmark_api(N):
    """
    Measure average execution time and average memory usage
    for both methods on input of size N×2.
    Returns: (avg_time_v1, avg_mem_v1, avg_time_v2, avg_mem_v2)
    """
    times_v1, times_v2 = [], []
    mems_v1, mems_v2   = [], []

    for _ in range(10):
        A = np.random.rand(N, 2).astype(np.float32)

        # --- method_v1 ---
        mem_before = get_memory_usage()
        t1 = timeit.timeit(lambda: method_v1(A), number=1)
        mem_after  = get_memory_usage()
        times_v1.append(t1)
        mems_v1.append(mem_after - mem_before)

        # --- method_v2 ---
        mem_before = get_memory_usage()
        t2 = timeit.timeit(lambda: method_v2(A), number=1)
        mem_after  = get_memory_usage()
        times_v2.append(t2)
        mems_v2.append(mem_after - mem_before)

    avg_time_v1 = sum(times_v1) / len(times_v1)
    avg_mem_v1  = sum(mems_v1)  / len(mems_v1)
    avg_time_v2 = sum(times_v2) / len(times_v2)
    avg_mem_v2  = sum(mems_v2)  / len(mems_v2)

    return avg_time_v1, avg_mem_v1, avg_time_v2, avg_mem_v2

# List of input sizes to test
test_sizes = [10, 100, 1000, 10000]

# Prepare a dictionary to hold results
data = {
    "api1": api1,
    "api2": api2,
    "package": package,
    "Description": description
}

# Check substitutability across all scales
substitutable = True
for N in test_sizes:
    A    = np.random.rand(N, 2).astype(np.float32)
    out1 = method_v1(A)
    out2 = method_v2(A)
    if out1.shape != out2.shape or not np.allclose(out1, out2, atol=1e-5):
        substitutable = False
        print(f"Output mismatch at N={N}, skipping benchmark.")
        break

data["Substitutable"] = "Yes" if substitutable else "No"

# If outputs match for all scales, run benchmarks
if substitutable:
    for i, N in enumerate(test_sizes, start=1):
        t1, m1, t2, m2 = benchmark_api(N)
        data[f"time{i}_1"]   = t1
        data[f"memory{i}_1"] = m1
        data[f"time{i}_2"]   = t2
        data[f"memory{i}_2"] = m2
else:
    print("APIs are not substitutable for all tested scales; benchmark skipped.")

# Append results to Excel file (create if missing)
df = pd.DataFrame([data])
if os.path.exists(output_file):
    existing = pd.read_excel(output_file, engine="openpyxl")
    df = pd.concat([existing, df], ignore_index=True)
df.to_excel(output_file, index=False, engine="openpyxl")

print(f"Test completed, results appended to {output_file}")
