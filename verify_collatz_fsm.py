import multiprocessing as mp
from collections import Counter

def get_state(x):
    mod9 = x % 9
    parity = 'Even' if x % 2 == 0 else 'Odd'

    C = {1, 2, 4}
    divisible_by_3 = (x % 3 == 0)

    is_P = (x % 6 == 0)
    is_R = divisible_by_3 and not is_P

    is_I = (mod9 == 1) and ((x - 1) // 9 % 2 == 1) and not divisible_by_3
    is_X = not divisible_by_3 and (x not in C) and not is_I
    is_XC = is_X or (x in C)

    if is_P:
        return 'S_P'
    elif is_R:
        return 'S_R'

    if mod9 == 1:
        if is_I and parity == 'Even': return 'S1'
        if is_XC and parity == 'Odd': return 'S2'
    elif mod9 == 2:
        if is_XC and parity == 'Even': return 'S3'
        if is_X and parity == 'Odd': return 'S4'
    elif mod9 == 4:
        if is_XC and parity == 'Even': return 'S5'
        if is_X and parity == 'Odd': return 'S6'
    elif mod9 == 5:
        if is_X and parity == 'Even': return 'S7'
        if is_X and parity == 'Odd': return 'S8'
    elif mod9 == 7:
        if is_X and parity == 'Even': return 'S9'
        if is_X and parity == 'Odd': return 'S10'
    elif mod9 == 8:
        if is_X and parity == 'Even': return 'S11'
        if is_X and parity == 'Odd': return 'S12'

    return 'Undefined'

def verify_collatz(start):
    current = start
    confined = True
    incorrect_cycle_entry = 0
    incorrect_S11_entry = 0

    while current != 1:
        state = get_state(current)
        if state == 'Undefined':
            confined = False

        prev = current
        current = current // 2 if current % 2 == 0 else 3 * current + 1

        if current == 4 and prev != 8:
            incorrect_cycle_entry += 1

        if current == 4 and prev == 8 and get_state(prev) != 'S11':
            incorrect_S11_entry += 1

    return (start, confined, incorrect_cycle_entry, incorrect_S11_entry)

def worker(rng):
    stage_counts = Counter({'S_P-R': 0, 'S_1-12': 0})
    confined_violations = 0
    incorrect_cycle_entries = 0
    incorrect_S11_entries = 0
    max_steps = (0, 0)

    for start in rng:
        stage = get_state(start)
        if stage in ['S_P', 'S_R']:
            stage_counts['S_P-R'] += 1
        else:
            stage_counts['S_1-12'] += 1

        steps, curr = 0, start
        while curr != 1:
            curr = curr // 2 if curr % 2 == 0 else 3 * curr + 1
            steps += 1

        if steps > max_steps[1]:
            max_steps = (start, steps)

        _, confined, ice, ise = verify_collatz(start)
        confined_violations += not confined
        incorrect_cycle_entries += ice
        incorrect_S11_entries += ise

    return (stage_counts, confined_violations, incorrect_cycle_entries, incorrect_S11_entries, max_steps)

def main(max_value=10000000, workers=mp.cpu_count()):
    ranges = [range(i, max_value + 1, workers) for i in range(1, workers + 1)]

    with mp.Pool(workers) as pool:
        results = pool.map(worker, ranges)

    total_stages = Counter()
    confined_violations = incorrect_cycle_entries = incorrect_S11_entries = 0
    max_steps = (0, 0)

    for res in results:
        sc, cv, ice, ise, ms = res
        total_stages += sc
        confined_violations += cv
        incorrect_cycle_entries += ice
        incorrect_S11_entries += ise
        if ms[1] > max_steps[1]:
            max_steps = ms

    print("Verification Summary:")
    print("Total Tested:", max_value)
    print("Stage Counts:", dict(total_stages))
    print("Confined Violations:", confined_violations)
    print("Incorrect Cycle Entries:", incorrect_cycle_entries)
    print("Incorrect S11 Entry Values:", incorrect_S11_entries)
    print("Max Steps:", max_steps[1])
    print("Number with Max Steps:", max_steps[0])

if __name__ == "__main__":
    main()
