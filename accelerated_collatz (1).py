def accelerated_collatz(n):
    if n % 4 == 1 or n % 8 == 5:
        return (3*n + 1) // 4
    else: # n % 4 == 3 or n % 8 == 7 or n % 8 == 3 (which simplifies to n % 4 == 3 for odd n)
        return (3*n + 1) // 2

def verify_cp_ncp(limit):
    samples_tested = 0
    error_found = False
    for n in range(3, limit, 2): # Check odd numbers from 3 up to limit
        samples_tested += 1
        cp_class = (n % 4 == 1) or (n % 8 == 5)
        ncp_class = (n % 4 == 3)

        t_star_n = accelerated_collatz(n)

        if cp_class:
            if not (t_star_n < n):
                print(f"Error: CP class number {n} should have T*(n) < n, but T*(n) = {t_star_n}")
                error_found = True
                break
        elif ncp_class:
            if not (t_star_n >= n):
                print(f"Error: NCP class number {n} should have T*(n) >= n, but T*(n) = {t_star_n}")
                error_found = True
                break
    if not error_found:
        print(f"Verification: CP/NCP classifications and T*(n) properties hold for {samples_tested} odd numbers tested up to n = {limit}.")
        return True
    else:
        print(f"Verification Failed after testing {samples_tested} samples. Error found as indicated above.")
        return False

limit_to_check = 100000
verify_cp_ncp(limit_to_check)