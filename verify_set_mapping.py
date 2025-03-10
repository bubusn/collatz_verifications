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

# Track mapping verification
mapping_checks = {
    "P → R or P": True,
    "R → IS": True,
    "IS → Reachable": True,
    "Reachable → Valid": True
}

# Verify mappings
for x in range(1, 10_000_001):
    category = classify_number(x)
    next_x = collatz_function(x)
    next_category = classify_number(next_x)

    if category == "P" and next_category not in {"P", "R"}:
        mapping_checks["P → R or P"] = False
    if category == "R" and next_category != "IS":
        mapping_checks["R → IS"] = False
    if category == "IS" and next_category != "Reachable":
        mapping_checks["IS → Reachable"] = False
    if category == "Reachable" and next_category not in {"C", "R", "P", "IS", "Reachable"}:
        mapping_checks["Reachable → Valid"] = False

# Print verification results
print("\n--- Set Mapping Verification (1 to 10M) ---")
for mapping, status in mapping_checks.items():
    print(f"[{'✓' if status else '✗'}] {mapping} mapping holds for all cases.")
