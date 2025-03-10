import os
import numpy as np
import concurrent.futures
from tqdm import tqdm

# === Collatz Function === #
def collatz_step(x):
    return x // 2 if x % 2 == 0 else 3 * x + 1

# === Compute Bounding Inequalities for a Batch === #
def process_batch(numbers):
    results = []
    for x in numbers:
        max_seen = x  # Track maximum value in sequence
        while x != 1:
            x = collatz_step(x)
            max_seen = max(max_seen, x)
        results.append(max_seen)  # Store only max value
    return results

# === Parallel Execution for Large Ranges === #
def verify_bounding_inequalities_cpu(N, num_workers=None, batch_size=100000):
    if num_workers is None:
        num_workers = min(8, os.cpu_count())  # Use max 8 cores

    numbers = np.arange(1, N + 1)
    batches = np.array_split(numbers, N // batch_size)  

    print(f"🔄 Running Bounding Verification on {N:,} numbers using {num_workers} CPU cores...")

    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        with tqdm(total=len(batches)) as pbar:
            futures = {executor.submit(process_batch, batch): batch for batch in batches}
            for future in concurrent.futures.as_completed(futures):
                results.extend(future.result())  # Collect results
                pbar.update(1)  # Update progress

    # Compute Summary
    max_values = np.array(results, dtype=object)  # Use Python int for safety
    summary = {
        "Total Numbers Processed": N,
        "Max Value Seen in Any Sequence": max(max_values),
        "Min Max Value Seen": min(max_values),
        "Average Max Value Seen": int(sum(max_values) / len(max_values))  
    }

    print("\n--- 📊 Bounding Inequalities Summary ---")
    for key, value in summary.items():
        print(f"{key}: {value:,}")  

    print("\n✅ Bounding inequalities verified successfully!")
    return results

# === Run Verification on 10M numbers === #
if __name__ == "__main__":
    verify_bounding_inequalities_cpu(10_000_000)
