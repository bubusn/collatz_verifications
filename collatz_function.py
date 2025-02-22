def collatz_function(n):
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1

def accelerated_collatz_function_odd_iterate(n):
    """Accelerated Collatz for odd iterates."""
    val = 3 * n + 1
    v = 0
    while val % 2 == 0:
        val //= 2
        v += 1
    return val, v

def get_odd_collatz_sequence(start_n, limit=1000):
    """Generates a Collatz sequence of odd iterates up to a limit or until it nears 1."""
    odd_sequence = []
    current_n = start_n
    odd_sequence.append(current_n)
    for _ in range(limit):
        next_odd_n, _ = accelerated_collatz_function_odd_iterate(current_n)
        if next_odd_n in [1, 5]: # Heuristic stop to avoid long sequences near 1
            break # Stop when sequence likely heading to trivial cycle quickly
        odd_sequence.append(next_odd_n)
        current_n = next_odd_n
    return odd_sequence

# 1. Verification of Congruence 3 mod 4 for Non-Decreasing Odd Steps
def verify_congruence_3_mod_4():
    non_decreasing_steps_count = 0
    congruent_3_mod_4_count = 0
    start_range_max = 100000
    sample_size = 15001 # Approximately

    tested_count = 0
    for start_num in range(101, start_range_max + 1, 2): # Test odd starting numbers > 100
        if tested_count >= sample_size:
            break
        odd_seq = get_odd_collatz_sequence(start_num)
        for i in range(len(odd_seq) - 1):
            a_k = odd_seq[i]
            a_k_plus_1 = odd_seq[i+1]
            if a_k_plus_1 >= a_k:
                non_decreasing_steps_count += 1
                if a_k % 4 == 3:
                    congruent_3_mod_4_count += 1
        tested_count += 1

    percentage_3_mod_4 = (congruent_3_mod_4_count / non_decreasing_steps_count) * 100 if non_decreasing_steps_count > 0 else 0

    print("\nVerification of Congruence 3 mod 4 for Non-Decreasing Odd Steps:")
    print(f"Total non-decreasing odd steps (with a_k > 100) observed: {non_decreasing_steps_count}")
    print(f"Number of times a_k ≡ 3 (mod 4) in these steps: {congruent_3_mod_4_count}")
    print(f"Percentage of non-decreasing steps with a_k ≡ 3 (mod 4): {percentage_3_mod_4:.2f}%")
    return non_decreasing_steps_count, congruent_3_mod_4_count, percentage_3_mod_4

# 2. Verification of Congruence Transition from 3 mod 8 to 1 mod 4
def verify_congruence_transition_3_mod_8_to_1_mod_4():
    start_j_range = range(10000, 20001)
    tested_count = len(start_j_range)
    valid_transitions_count = 0

    for j in start_j_range:
        a_k = 8 * j + 3
        a_k_plus_1, _ = accelerated_collatz_function_odd_iterate(a_k)
        if (3*a_k + 1) / 2 >= a_k and (3*a_k + 1) / 2 == a_k_plus_1 * (2**1): # Check if division by 2^1
             if a_k_plus_1 % 4 == 1:
                 valid_transitions_count += 1

    percentage_valid_transitions = (valid_transitions_count / tested_count) * 100 if tested_count > 0 else 0

    print("\nVerification of Congruence Transition 3 mod 8 to 1 mod 4:")
    print(f"Starting a_k = 8j+3 tested (j=10000 to 20000): {tested_count}")
    print(f"Number of cases where a_{{k+1}} = (3a_k+1)/2 >= a_k and a_{{k+1}} ≡ 1 (mod 4): {valid_transitions_count}")
    print(f"Percentage of valid transitions: {percentage_valid_transitions:.2f}%")
    return tested_count, valid_transitions_count, percentage_valid_transitions


# 3. Re-verification of Decreasing Trend for Odd Integers Congruent to 1 mod 4
def verify_decreasing_trend_1_mod_4():
    tested_count = 0
    decreasing_count = 0
    max_n_test = 100000

    for n in range(1, max_n_test + 1, 4): # Test odd integers n ≡ 1 (mod 4)
        if n <= 1: # Exclude n=1 as per Lemma condition n > 1
            continue
        t_star_n, _ = accelerated_collatz_function_odd_iterate(n)
        tested_count += 1
        if t_star_n < n:
            decreasing_count += 1

    percentage_decreasing = (decreasing_count / tested_count) * 100 if tested_count > 0 else 0

    print("\nRe-verification of Decreasing Trend for Odd Integers Congruent to 1 mod 4:")
    print(f"Odd n ≡ 1 (mod 4) tested: {tested_count}")
    print(f"Number of cases where T*(n) < n: {decreasing_count}")
    print(f"Percentage of cases where T*(n) < n: {percentage_decreasing:.2f}%")
    return tested_count, decreasing_count, percentage_decreasing


if __name__ == "__main__":
    results_1 = verify_congruence_3_mod_4()
    results_2 = verify_congruence_transition_3_mod_8_to_1_mod_4()
    results_3 = verify_decreasing_trend_1_mod_4()

    print("\n--- Summary for LaTeX Table ---")
    print("\\multicolumn{2}{|c|}{\\textbf{Congruence 3 mod 4 for Non-Decreasing Steps}} \\")
    print("\\hline")
    print(f"Total non-decreasing odd steps (with $a_k > 100$) observed & {results_1[0]} \\\\")
    print("\\hline")
    print(f"Steps with $a_k \\equiv 3 \\pmod{{4}}$ & {results_1[1]} \\\\")
    print("\\hline")
    print(f"Percentage $\\equiv 3 \\pmod{{4}}$ & {results_1[2]:.2f}\\% \\\\")
    print("\\hline")
    print("\\multicolumn{2}{|c|}{\\textbf{Congruence Transition 3 mod 8 to 1 mod 4}} \\")
    print("\\hline")
    print(f"Starting $a_k = 8j+3$ tested (j=10000 to 20000) & {results_2[0]} \\\\")
    print("\\hline")
    print(f"Valid transitions to $a_{{k+1}} \\equiv 1 \\pmod{{4}}$ & {results_2[1]} \\\\")
    print("\\hline")
    print(f"Percentage of valid transitions & {results_2[2]:.2f}\\% \\\\")
    print("\\hline")
    print("\\multicolumn{2}{|c|}{\\textbf{Decreasing Trend for $n \\equiv 1 \\pmod{{4}}$}} \\")
    print("\\hline")
    print(f"Odd $n \\equiv 1 \\pmod{{4}}$ tested & {results_3[0]} \\\\")
    print("\\hline")
    print(f"Cases with $T^*(n) < n$ & {results_3[1]} \\\\")
    print("\\hline")
    print(f"Percentage of cases with $T^*(n) < n$ & {results_3[2]:.2f}\\% \\\\")
    print("\\hline")