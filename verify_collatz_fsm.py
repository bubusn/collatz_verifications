import multiprocessing as mp
from collections import Counter
import time
from functools import partial

# --- State Definitions (Corrected) ---

def get_state(x):
    """Determines the FSM state (S_P, S_R, S_C1-C4, S1-S12) for a given integer x."""
    if not isinstance(x, int) or x < 1:
        return 'Undefined_Error (Non-positive)'

    if x == 1: return 'S_C1'
    if x == 2: return 'S_C2'
    if x == 4: return 'S_C4'

    try:
        mod9 = x % 9
        parity = 'Even' if x % 2 == 0 else 'Odd'

        is_P = (x % 6 == 0)
        if is_P: return 'S_P'
        is_R = (x % 3 == 0)
        if is_R: return 'S_R'

        is_I = (mod9 == 1) and (((x - 1) // 9) % 2 == 1)

        if is_I:
             if parity != 'Even' or mod9 != 1: return 'Error_I_Def'
             return 'S1'

        if mod9 == 1:
             if parity != 'Odd': return 'Error_X1_Def'
             return 'S2'
        elif mod9 == 2:
             return 'S3' if parity == 'Even' else 'S4'
        elif mod9 == 4:
             return 'S5' if parity == 'Even' else 'S6'
        elif mod9 == 5:
             return 'S7' if parity == 'Even' else 'S8'
        elif mod9 == 7:
             return 'S9' if parity == 'Even' else 'S10'
        elif mod9 == 8:
             return 'S11' if parity == 'Even' else 'S12'

        print(f"Warning: Unhandled case for get_state({x})")
        return 'Undefined_Error (Unhandled Case)'

    except Exception as e:
        print(f"Error in get_state({x}): {e}")
        return f'Undefined_Error ({e})'

# --- FSM Transition Rules (Based on Lemma 6.8) ---

TRANSITION_RULES = {
    # S_P omitted: Not a single-step check
    'S_R': frozenset({'S1'}),
    'S1': frozenset({'S7', 'S8'}),
    'S2': frozenset({'S5'}),
    'S3': frozenset({'S1', 'S2'}),
    'S4': frozenset({'S9'}),
    'S5': frozenset({'S3', 'S4'}),
    'S6': frozenset({'S5'}),
    'S7': frozenset({'S9', 'S10'}),
    'S8': frozenset({'S9'}),
    'S9': frozenset({'S11', 'S12'}),
    'S10': frozenset({'S5'}),
    'S11': frozenset({'S5', 'S6', 'S_C4'}), # Includes exit
    'S12': frozenset({'S9'}),
    'S_C1': frozenset({'S_C4'}),
    'S_C2': frozenset({'S_C1'}),
    'S_C4': frozenset({'S_C2'}),
}

# --- Combined Trace and Verification Function ---

def trace_and_verify_all(start, rules):
    """
    Traces sequence, counts steps to 1, checks confinement, gateway rules,
    and state transition conformance. Returns status and details.
    """
    current = start
    steps = 0
    violation_type = None # Type of first violation found
    violation_details = None # Detailed info about first violation

    MAX_ITERATIONS = 10000 # Safety break

    # --- Determine Initial Stage ---
    start_state = get_state(start)
    if 'Undefined' in start_state or 'Error' in start_state:
        violation_type = 'Confined'
        violation_details = (start, None, start_state, None, None, "Undefined start state")
        initial_stage = 'Undefined'
        steps = -1 # Indicate error
        return start, initial_stage, steps, violation_type, violation_details
    elif start_state in ['S_P', 'S_R']:
        initial_stage = 'S_P-R'
    elif start_state in ['S_C1', 'S_C2', 'S_C4']:
        initial_stage = 'S_C'
    else:
        initial_stage = 'S_1-12'

    # --- Trace Sequence and Verify ---
    for _ in range(MAX_ITERATIONS):
        prev = current
        prev_state = get_state(prev) # State before transition

        # 1. Check Confinement (State Validity) before step
        if 'Undefined' in prev_state or 'Error' in prev_state:
            violation_type = 'Confined'
            violation_details = (start, prev, prev_state, None, None, "Undefined state encountered")
            steps = -1
            break

        # 2. Check Stop Condition (Reached Cycle Stage)
        if prev_state in ['S_C1', 'S_C2', 'S_C4']:
            # We need steps to 1, so continue if not 1 yet, but stop checking transitions
            if prev == 1:
                 break # Correctly finished at 1
            # Apply Collatz within cycle without further checks
            current = prev // 2 if prev % 2 == 0 else 3 * prev + 1
            steps += 1
            continue # Continue loop until current is 1

        # 3. Apply Collatz Rule
        if prev % 2 == 0:
            current = prev // 2
        else:
            # Basic overflow check
            if prev > (2**63 - 2) // 3:
                violation_type = 'Error'
                violation_details = (start, prev, prev_state, None, None, "Potential overflow")
                steps = -1
                break
            current = 3 * prev + 1
        steps += 1

        current_state = get_state(current)

        # 4. Check Confinement (State Validity) after step
        if 'Undefined' in current_state or 'Error' in current_state:
            violation_type = 'Confined'
            violation_details = (start, prev, prev_state, current, current_state, "Undefined state reached")
            steps = -1
            break

        # 5. Check State Transition Rule Conformance
        # Skip check *from* S_P as its rule isn't single-step
        if prev_state != 'S_P':
            expected_successors = rules.get(prev_state)
            if expected_successors is None:
                 violation_type = 'Error'
                 violation_details = (start, prev, prev_state, current, current_state, "Unknown prev_state in rules")
                 steps = -1
                 break
            if current_state not in expected_successors:
                 violation_type = 'Transition'
                 violation_details = (start, prev, prev_state, current, current_state, expected_successors)
                 steps = -1
                 break # Stop on first violation

        # 6. Check Gateway Conditions (only relevant if transition was otherwise valid)
        # Check if we just entered state S_C4 (which represents 4)
        if current_state == 'S_C4':
            if prev != 8 and prev_state != 'S_C1': # Reaching 4 from anywhere unexpected?
                violation_type = 'Gateway Entry'
                violation_details = (start, prev, prev_state, current, current_state, "Reached S_C4 not from S11(8) or S_C1(1)")
                steps = -1
                break
            if prev == 8 and prev_state != 'S11': # Reaching 4 from 8, but 8 wasn't S11?
                violation_type = 'Gateway S11'
                violation_details = (start, prev, prev_state, current, current_state, "Reached S_C4 from 8, but state(8) was not S11")
                steps = -1
                break

        # Check if loop should terminate (reached 1)
        if current == 1:
            break

    # Check if loop exited due to max iterations
    else: # This else belongs to the for loop, executed if break was not called
        violation_type = 'Error'
        violation_details = (start, prev, prev_state, current, current_state, f"Exceeded {MAX_ITERATIONS} iterations")
        steps = -1

    # Determine final status
    status = 'OK' if violation_type is None else violation_type

    return start, initial_stage, steps, status, violation_details

# --- Parallel Worker ---

def worker_combined(rng, rules):
    """Processes range, returning counts and violation details."""
    stage_counts = Counter({'S_P-R': 0, 'S_1-12': 0, 'S_C': 0, 'Undefined': 0})
    max_steps_info = (0, 0) # (start_num, steps)
    violations = Counter() # Count types of violations
    first_violation_details = {} # Store details of first violation of each type

    for start_num in rng:
        start, initial_stage, steps, status, details = trace_and_verify_all(start_num, rules)

        stage_counts[initial_stage] += 1

        if status == 'OK':
            if steps > max_steps_info[1]:
                max_steps_info = (start, steps)
        else:
            violations[status] += 1
            # Store details only for the first occurrence of each violation type
            if status not in first_violation_details:
                 first_violation_details[status] = details

    return stage_counts, max_steps_info, violations, first_violation_details

# --- Main Execution ---

def main_combined(max_value=1000000, num_workers=8):
    """Sets up and runs the combined verification."""

    max_possible_workers = mp.cpu_count()
    num_workers = max(1, min(num_workers, max_possible_workers, max_value))

    ranges = [range(i, max_value + 1, num_workers) for i in range(1, num_workers + 1)]
    ranges = [r for r in ranges if len(r) > 0]
    num_workers = len(ranges)
    if num_workers == 0:
        print("Max value too small.")
        return

    print(f"Starting combined verification up to {max_value} using {num_workers} workers...")
    start_time = time.time()

    worker_func = partial(worker_combined, rules=TRANSITION_RULES)

    with mp.Pool(num_workers) as pool:
        results = pool.map(worker_func, ranges)

    end_time = time.time()
    total_time = end_time - start_time
    print(f"Processing finished in {total_time:.2f} seconds.")

    # Aggregate results
    total_stages = Counter()
    global_max_steps_info = (0, 0)
    total_violations = Counter()
    all_first_violation_details = {}

    for sc, ms, v, fvd in results:
        total_stages += sc
        if ms[1] > global_max_steps_info[1]:
            global_max_steps_info = ms
        total_violations += v
        # Keep the first reported details for each type across all workers
        for v_type, details in fvd.items():
            if v_type not in all_first_violation_details:
                 all_first_violation_details[v_type] = details

    # --- Print Summary ---
    print("\n--- Combined Verification Summary ---")
    total_tested = sum(total_stages.values())
    print(f"Range Tested: 1 to {max_value} (Processed: {total_tested})")
    print("Initial Stage Counts:", dict(total_stages))
    print("Max Steps to reach 1:", global_max_steps_info[1])
    print("Number yielding Max Steps:", global_max_steps_info[0])
    print("\nViolation Counts by Type:")
    if not total_violations:
        print("  None")
    else:
        for v_type, count in total_violations.items():
            print(f"  {v_type}: {count}")
    print("-----------------------------------")

    # --- Final Verdict & Details ---
    total_violation_count = sum(total_violations.values())
    if total_violation_count == 0 and total_tested == max_value:
        print("\nSUCCESS: All tested sequences conform to FSM definitions and transitions.")
    elif total_violation_count == 0:
         print("\nVerification completed (possibly partial range). No violations detected in processed range.")
    else:
        print(f"\n*** ERROR: {total_violation_count} violation(s) DETECTED! ***")
        print("Showing details for the first violation of each type found:")
        for v_type, details in all_first_violation_details.items():
             print(f"\n  Violation Type: {v_type}")
             if v_type == 'Transition':
                  start, prev, p_state, curr, c_state, expected = details
                  print(f"    Start={start}")
                  print(f"    Step: {prev} (State: {p_state}) -> {curr} (State: {c_state})")
                  print(f"    Expected next state(s) for {p_state}: {expected}")
             elif v_type == 'Gateway Entry':
                  start, prev, p_state, curr, c_state, msg = details
                  print(f"    Start={start}")
                  print(f"    Step: {prev} (State: {p_state}) -> {curr} (State: {c_state})")
                  print(f"    Reason: {msg}")
             elif v_type == 'Gateway S11':
                  start, prev, p_state, curr, c_state, msg = details
                  print(f"    Start={start}")
                  print(f"    Step: {prev} (State: {p_state}) -> {curr} (State: {c_state})")
                  print(f"    Reason: {msg}")
             elif v_type == 'Confined':
                  start, num, state, _, _, msg = details
                  print(f"    Start={start}")
                  print(f"    Number: {num}, State: {state}")
                  print(f"    Reason: {msg}")
             elif v_type == 'Error':
                  start, prev, p_state, curr, c_state, msg = details
                  print(f"    Start={start}")
                  print(f"    Context: Prev={prev}({p_state}), Curr={curr}({c_state})")
                  print(f"    Reason: {msg}")
             else: # Generic fallback
                  print(f"    Details: {details}")
        print("-" * 10)


if __name__ == "__main__":
    # Set the maximum value to test here
    TEST_UP_TO = 10000000 # Example: 1 Million
    # TEST_UP_TO = 10000000 # Example: 10 Million
    # TEST_UP_TO = 1000 # Small test

    # Set number of workers
    NUM_WORKERS = 8

    main_combined(max_value=TEST_UP_TO, num_workers=NUM_WORKERS)
