def collatz_like_step(o):
    """Computes the next iterate of an odd integer o using (3o + 1) / 2."""
    return (3 * o + 1) // 2

def steps_to_exit_3_mod_4(start, max_steps=1000):
    """Counts steps for an odd number o ≡ 7 (mod 12) to fall out of 3 mod 4."""
    o = start
    steps = 0

    seen = set()  # Track visited numbers to detect loops

    while steps < max_steps:
        o_next = collatz_like_step(o)
        residue_4 = o_next % 4
        steps += 1

        # Stop when the number is no longer 3 mod 4
        if residue_4 != 3:
            return steps

        # Detect potential cycles
        if o_next in seen:
            return -1  # Indicates possible infinite cycle

        seen.add(o_next)
        o = o_next  # Move to the next iterate

    return -1  # Return -1 if max_steps exceeded (suggesting infinite behavior)

# Test a larger range of numbers o ≡ 7 (mod 12)
N = 1000000  # Test up to numbers around 10^6
num_tests = 10000  # Number of numbers to check

step_counts = []
largest_o = 0
max_steps = 0
total_steps = 0

print(f"{'o':>10}  {'Steps to exit 3 mod 4':>25}")
print("-" * 40)

for i in range(num_tests):
    o_start = 7 + 12 * i
    if o_start > N:
        break  # Stop if we exceed the testing range
    steps = steps_to_exit_3_mod_4(o_start)

    print(f"{o_start:10}  {steps:25}")

    if steps > max_steps:
        max_steps = steps
        largest_o = o_start

    total_steps += steps
    step_counts.append(steps)

# Summary Statistics
avg_steps = total_steps / len(step_counts)

print("\nSummary Statistics:")
print(f"Total numbers tested: {len(step_counts)}")
print(f"Max steps observed: {max_steps} (for o = {largest_o})")
print(f"Min steps observed: {min(step_counts)}")
print(f"Average steps: {avg_steps:.2f}")
