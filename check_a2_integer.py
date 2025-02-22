def check_A2_integer(limit):
    samples_tested = 0
    error_found = False
    for k in range(1, limit // 6 + 2): # Iterate for odd multiples of 3 up to limit
        x = 6*k + 3
        samples_tested += 1
        numerator = 2*x - 1
        if numerator % 3 == 0: # Check if divisible by 3
            a2 = numerator / 3
            if a2 == int(a2): # Check if it's an integer
                print(f"Error: A'_2({x}) = {a2} is an integer for x = {x} which is congruent to 3 mod 6.")
                error_found = True
                break # Stop at the first error
    if not error_found:
        print(f"Verification: A'_2(x) is never an integer for {samples_tested} odd multiples of 3 tested up to x = {limit}.")
        return True
    else:
        print(f"Verification Failed after testing {samples_tested} samples. Error found as indicated above.")
        return False

limit_to_check = 1000000
check_A2_integer(limit_to_check)