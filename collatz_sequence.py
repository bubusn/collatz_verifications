def collatz_sequence(n):
    sequence = [n]
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3*n + 1
        sequence.append(n)
    return sequence

def verify_collatz_conjecture(limit):
    samples_tested = 0
    error_found = False
    for start_n in range(1, limit + 1):
        samples_tested += 1
        sequence = collatz_sequence(start_n)
        if sequence[-1] != 1:
            print(f"Error: Collatz sequence for {start_n} does not reach 1. Sequence: {sequence}") # Print sequence for debugging
            error_found = True
            break
    if not error_found:
        print(f"Verification: All Collatz sequences reach 1 for {samples_tested} starting numbers tested up to n = {limit}.")
        return True
    else:
        print(f"Verification Failed after testing {samples_tested} samples. Error found as indicated above.")
        return False

limit_to_check = 100000
verify_collatz_conjecture(limit_to_check)