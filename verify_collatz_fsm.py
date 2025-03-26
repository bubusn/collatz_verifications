import multiprocessing as mp
from collections import Counter
import time # Added for basic timing

# --- State Definitions ---

def get_state(x):
    """Determines the FSM state (S_P, S_R, S_C1-C4, S1-S12) for a given integer x."""
    # Handle Cycle States First
    if x == 1: return 'S_C1'
    if x == 2: return 'S_C2'
    if x == 4: return 'S_C4'

    # --- Check properties needed for other states ---
    mod9 = x % 9
    parity = 'Even' if x % 2 == 0 else 'Odd'

    # Handle Initial States (Divisible by 3)
    is_P = (x % 6 == 0) # Even multiple of 3
    if is_P:
        return 'S_P'
    # If not P, but divisible by 3, must be R (Odd multiple of 3)
    is_R = (x % 3 == 0)
    if is_R:
        return 'S_R'

    # Handle Transient States (S1-S12) - know x is not P, R, C
    # Check if x is in Set I = {9j+1 | j odd}
    # If x=9j+1 -> x-1=9j -> j=(x-1)//9. Need j odd.
    # Note: x % 3 != 0 is guaranteed if not P/R.
    # Note: x in I implies x = 1 mod 9 and x is Even.
    is_I = (mod9 == 1) and (((x - 1) // 9) % 2 == 1)

    # S1 (I, Even) - By definition, if x is in I, it MUST be Even and 1 mod 9
    if is_I:
        # Optional sanity check: if parity != 'Even' or mod9 != 1: return 'Error_I_Def'
        return 'S1'

    # If not P, R, C, I, it must be X. State depends on mod9 and parity.
    if mod9 == 1: # Must be Odd if X (Even case covered by S1)
        # Optional sanity check: if parity != 'Odd': return 'Error_X1_Def'
        return 'S2' # State (1, X, Odd)
    elif mod9 == 2:
        return 'S3' if parity == 'Even' else 'S4' # States (2, X, E/O)
    elif mod9 == 4:
        return 'S5' if parity == 'Even' else 'S6' # States (4, X, E/O)
    elif mod9 == 5:
        return 'S7' if parity == 'Even' else 'S8' # States (5, X, E/O)
    elif mod9 == 7:
        return 'S9' if parity == 'Even' else 'S10' # States (7, X, E/O)
    elif mod9 == 8:
        return 'S11' if parity == 'Even' else 'S12' # States (8, X, E/O)

    # This should be unreachable if partitioning and logic are correct
    print(f"Warning: Undefined state for x = {x}") # Add warning if reached
    return 'Undefined_Error'

# --- Trace and Verification ---

def trace_and_verify(start):
    """
    Traces the Collatz sequence from start, counts steps, checks confinement
    to defined states, and verifies gateway conditions.
    """
    current = start
    steps = 0
    confined = True
    incorrect_cycle_entry = 0 # Count instances of x -> 4 where x != 8 and x != 1
    incorrect_S11_entry = 0 # Count instances of 8 -> 4 where state(8) was not S11

    # --- Determine Initial Stage ---
    start_state = get_state(start)
    if start_state == 'Undefined_Error':
        confined = False # Error in state definition if reached
        initial_stage = 'Undefined'
    elif start_state in ['S_P', 'S_R']:
        initial_stage = 'S_P-R'
    elif start_state in ['S_C1', 'S_C2', 'S_C4']:
        initial_stage = 'S_C'
    else: # Must be S1-S12
        initial_stage = 'S_1-12'

    # --- Trace Sequence ---
    while current != 1: # Loop until convergence to 1
        prev = current
        prev_state = get_state(prev)

        # Check confinement before proceeding
        if prev_state == 'Undefined_Error':
            confined = False
            break

        # Apply Collatz
        if current % 2 == 0:
            current = current // 2
        else:
            # Check for potential overflow before multiplication
            if current > (2**63 - 2) // 3: # Basic check for typical 64-bit int
                 print(f"Warning: Potential overflow near {prev}. Stopping trace.")
                 confined = False # Treat as violation for safety
                 break
            current = 3 * current + 1
        steps += 1

        # Check Gateway conditions during the transition *to* current state
        # Did we just land on 4? Check where from.
        if current == 4:
            if prev != 8 and prev != 1: # Reaching 4 from anywhere else?
                incorrect_cycle_entry += 1
            if prev == 8 and prev_state != 'S11': # Reaching 4 from 8, but 8 wasn't S11?
                incorrect_S11_entry += 1

    # If loop terminated due to non-confinement, steps might not be to cycle
    if not confined:
         steps = -1 # Indicate abnormal termination

    return (start, initial_stage, steps, confined, incorrect_cycle_entry, incorrect_S11_entry)

# --- Parallel Worker ---

def worker(rng):
    """Processes a range of start values, returning aggregated statistics."""
    # Use more descriptive stage names if preferred
    stage_counts = Counter({'S_P-R': 0, 'S_1-12': 0, 'S_C': 0, 'Undefined': 0})
    total_confined_violations = 0
    total_incorrect_cycle_entries = 0
    total_incorrect_S11_entries = 0
    max_steps_info = (0, 0) # (start_num, steps)

    for start in rng:
         # Get all info from single trace
         _, initial_stage, steps, confined, ice, ise = trace_and_verify(start)

         # Count initial stage
         stage_counts[initial_stage] += 1

         # Update max steps (only consider valid, confined sequences)
         if confined and steps > max_steps_info[1]:
              max_steps_info = (start, steps)

         # Aggregate violations
         if not confined:
              total_confined_violations += 1
         total_incorrect_cycle_entries += ice
         total_incorrect_S11_entries += ise

    return (stage_counts, total_confined_violations, total_incorrect_cycle_entries, total_incorrect_S11_entries, max_steps_info)

# --- Main Execution ---

def main(max_value=1000000, workers=None):
    """
    Sets up parallel processing, runs verification, aggregates results,
    and prints summary.
    """
    if workers is None:
        workers = mp.cpu_count()
    # Ensure at least 1 worker and not more workers than tasks if max_value is small
    num_workers = max(1, min(workers, max_value))

    # Divide the range among workers
    ranges = [range(i, max_value + 1, num_workers) for i in range(1, num_workers + 1)]
    # Filter out empty ranges if max_value < num_workers
    ranges = [r for r in ranges if len(r) > 0]
    # Adjust num_workers if some ranges were empty
    num_workers = len(ranges)
    if num_workers == 0:
        print("Max value too small to test.")
        return

    print(f"Starting verification up to {max_value} using {num_workers} workers...")
    start_time = time.time()

    with mp.Pool(num_workers) as pool:
        results = pool.map(worker, ranges)

    end_time = time.time()
    print(f"Processing finished in {end_time - start_time:.2f} seconds.")

    # Aggregate results from all workers
    total_stages = Counter()
    global_confined_violations = 0
    global_incorrect_cycle_entries = 0
    global_incorrect_S11_entries = 0
    global_max_steps_info = (0, 0) # (start_num, steps)

    for res in results:
        sc, cv, ice, ise, ms = res
        total_stages += sc
        global_confined_violations += cv
        global_incorrect_cycle_entries += ice
        global_incorrect_S11_entries += ise
        # Find the overall max steps
        if ms[1] > global_max_steps_info[1]:
            global_max_steps_info = ms

    # --- Print Summary ---
    print("\n--- Verification Summary ---")
    total_tested = sum(total_stages.values()) # Count only numbers actually processed
    print(f"Range Tested: 1 to {max_value} (Processed: {total_tested})")
    print("Initial Stage Counts:", dict(total_stages))
    print("Confined Violations (State Undefined or Sequence Issue):", global_confined_violations)
    print("Incorrect Cycle Entries (x -> 4 where x != 8, x != 1):", global_incorrect_cycle_entries)
    print("Incorrect S11 Entry Values (8 -> 4 where state(8) != S11):", global_incorrect_S11_entries)
    print("Max Steps to reach {1,2,4}:", global_max_steps_info[1])
    print("Number yielding Max Steps:", global_max_steps_info[0])
    print("--------------------------")

    # --- Final Verdict ---
    if global_confined_violations > 0 or \
       global_incorrect_cycle_entries > 0 or \
       global_incorrect_S11_entries > 0:
        print("\n*** WARNING: Violations detected! Review FSM definitions, transitions, or code logic. ***")
    elif total_tested == max_value:
         print("\nVerification successful within the tested range. No violations detected.")
    else:
         print("\nVerification completed (possibly partial range). No violations detected in processed range.")


if __name__ == "__main__":
    # Set the maximum value to test here
    TEST_UP_TO = 10000000 # Example: 1 Million
    # TEST_UP_TO = 10000000 # Example: 10 Million (takes longer)

    main(max_value=TEST_UP_TO)
