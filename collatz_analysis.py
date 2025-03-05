
import random
import time
import numpy as np
from numba import njit, prange, cuda

@njit
def collatz_step(n):
    """Performs a single Collatz step (Numba-optimized)."""
    return n // 2 if n % 2 == 0 else 3 * n + 1

@njit
def two_adic_valuation(n):
    """Calculates the 2-adic valuation of n (Numba-optimized)."""
    if n == 0:
        return np.inf  # Use NumPy's infinity for consistency
    valuation = 0
    while n & 1 == 0:
        n >>= 1
        valuation += 1
    return valuation

@njit
def check_k_form(k, N_limit=100):  # Reduced N_limit for GPU
    """Optimized check for k form (Numba-optimized)."""
    nine_k_plus_8 = 9 * k + 8
    for N in range(4, N_limit + 1):
        power_of_2 = 1 << N
        if nine_k_plus_8 % power_of_2 == 0:
            x = nine_k_plus_8 // power_of_2
            if x & 1:
                return (True, N, x)
    return (False, None, None)

@njit
def collatz_sequence_analysis_single(start_value, max_steps=1000): #Reduced max_steps for GPU
    """Analyzes a *single* Collatz sequence (Numba-optimized)."""
    n = start_value
    num_odd_iterates = 0
    num_3mod4 = 0
    num_5mod6 = 0
    num_k_form_matches = 0
    max_v2 = 0
    converged = False
    max_steps_reached = False
    highest_value = n

    for _ in range(max_steps):
        if n == 1:
            converged = True
            break
        if n & 1:
            num_odd_iterates += 1
            if n % 4 == 3:
                num_3mod4 += 1
            if n % 6 == 5:
                num_5mod6 += 1
                k = (n - 5) // 6
                is_k_form, N, x = check_k_form(k)
                if is_k_form:
                    num_k_form_matches += 1
                    max_v2 = max(max_v2, two_adic_valuation(3*n + 1))
        highest_value = max(highest_value, n)
        n = collatz_step(n)
    else:
        max_steps_reached = True

    return (
        start_value,
        num_odd_iterates,
        num_3mod4,
        num_5mod6,
        num_k_form_matches,
        max_v2,
        converged,
        max_steps_reached,
        highest_value,
    )

@njit(parallel=True)
def collatz_sequence_analysis_parallel(start_values, max_steps=1000):
    """Analyzes multiple Collatz sequences in parallel (Numba-optimized)."""
    n = len(start_values)
    results = np.empty((n, 9), dtype=np.float64)  # Use float64 for max_v2 (can be inf)

    for i in prange(n):  # Use prange for parallel loops
        # Assign each element of the tuple individually
        (start_value,
         num_odd_iterates,
         num_3mod4,
         num_5mod6,
         num_k_form_matches,
         max_v2,
         converged,
         max_steps_reached,
         highest_value) = collatz_sequence_analysis_single(start_values[i], max_steps)

        results[i, 0] = start_value
        results[i, 1] = num_odd_iterates
        results[i, 2] = num_3mod4
        results[i, 3] = num_5mod6
        results[i, 4] = num_k_form_matches
        results[i, 5] = max_v2
        results[i, 6] = converged  # No need to cast
        results[i, 7] = max_steps_reached # No need to cast
        results[i, 8] = highest_value
    return results

def main():
    """Generates random starting values and analyzes their Collatz sequences."""
    num_tests = 10000000  # 100 million tests
    max_steps = 10000   # Accomodate long sequences
    random.seed(42)

    start_time = time.time()

    # Create a generator for starting values
    start_values_gen = (random.randint(1, 1000000) for _ in range(num_tests))

    # Convert the generator to a NumPy array for Numba compatibility
    start_values = np.fromiter(start_values_gen, dtype=np.int64)

    # Run the analysis in parallel
    results = collatz_sequence_analysis_parallel(start_values, max_steps)

    end_time = time.time()
    elapsed_time = end_time - start_time

    # Process results (convert NumPy array back to a list of dicts for consistency)
    results_summary = []
    for i in range(results.shape[0]): #Use results.shape[0]
        results_summary.append({
            "start_value": int(results[i, 0]), # Cast back to int
            "num_odd_iterates": int(results[i, 1]), # Cast back to int
            "num_3mod4": int(results[i, 2]), # Cast back to int
            "num_5mod6": int(results[i, 3]), # Cast back to int
            "num_k_form_matches": int(results[i, 4]), # Cast back to int
            "max_v2": results[i, 5],
            "converged": bool(results[i, 6]),
            "max_steps_reached": bool(results[i, 7]),
            "highest_value": int(results[i, 8]), # Cast back to int
        })

   # Overall Summary Statistics
    total_tests = len(results_summary)
    total_converged = sum(1 for r in results_summary if r["converged"])
    total_max_steps_reached = sum(1 for r in results_summary if r["max_steps_reached"])
    total_odd_iterates = sum(r["num_odd_iterates"] for r in results_summary)
    total_3mod4 = sum(r["num_3mod4"] for r in results_summary)
    total_5mod6 = sum(r["num_5mod6"] for r in results_summary)
    total_k_form_matches = sum(r["num_k_form_matches"] for r in results_summary)
    max_max_v2 = max(r["max_v2"] for r in results_summary)
    highest_max_val = max(r["highest_value"] for r in results_summary)

    print("Collatz Sequence Analysis Summary:")
    print(f"  Total tests: {total_tests}")
    print(f"  Converged within {max_steps} steps: {total_converged}")
    print(f"  Reached max steps ({max_steps}): {total_max_steps_reached}")
    print(f"  Total odd iterates: {total_odd_iterates}")
    print(f"  Total 3 (mod 4) odd iterates: {total_3mod4}")
    print(f"  Total 5 (mod 6) odd iterates: {total_5mod6}")
    print(f"  Total 5 (mod 6) iterates with matching k form: {total_k_form_matches}")
    print(f"  Highest 2-adic valuation observed: {max_max_v2}")
    print(f"  Highest value attained in a sequence: {highest_max_val}")
    print(f"  Total time taken: {elapsed_time:.2f} seconds")

    # Check for potential issues:
    if total_max_steps_reached > 0:
        print("\nWARNING: Some sequences reached the maximum step limit.  Increase max_steps for more thorough testing.")
    if total_5mod6 > 0 and total_k_form_matches == 0:
        print("\nWARNING: Found 5 (mod 6) iterates, but none matched the k-form. This indicates a potential problem.")

    failures = 0
    for r in results_summary:
        if r["num_3mod4"] > 0 and r["num_5mod6"] == 0:
            failures += 1
    if failures > 0:
        print(f"\nWARNING: Found cases with 3mod4, without 5mod6 {failures}")

    unbounded_indications = 0
    for r in results_summary:
        if not r["converged"] and not r["max_steps_reached"] :
            unbounded_indications +=1
        elif not r["converged"] and r["max_steps_reached"] and r["num_5mod6"] == r["num_k_form_matches"] and r["num_5mod6"]>0:
             unbounded_indications +=1
    if unbounded_indications > 0:
         print(f"\nWARNING: {unbounded_indications} possible unbounded sequences")

if __name__ == "__main__":
    main()
