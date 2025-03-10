def collatz_function(x):
    """Applies the Collatz function to x."""
    return x // 2 if x % 2 == 0 else 3 * x + 1

def classify_number(x):
    """Classifies x into C, R, P, IS, or Reachable."""
    if x in {1, 2, 4}:
        return "C"
    elif x % 3 == 0:
        return "R" if x % 2 == 1 else "P"
    elif x % 9 == 1:
        return "IS"
    else:
        return "Reachable"

# Track set counts
counts = {"C": 0, "R": 0, "P": 0, "IS": 0, "Reachable": 0}

# Classify numbers from 1 to 10,000,000
for x in range(1, 10_000_001):
    category = classify_number(x)
    counts[category] += 1

# Print classification results
print("--- Classification Results (1 to 10M) ---")
for key, value in counts.items():
    print(f"  {key}: {value} numbers")
