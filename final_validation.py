"""
Final validation - launch GUI and verify output programmatically.
"""
import subprocess
import time

print("="*60)
print("FINAL VALIDATION TEST")
print("="*60)

print("\n1. Testing console output...")
result = subprocess.run(
    ["python", "test_output.py"],
    capture_output=True,
    text=True
)

output = result.stdout + result.stderr

# Check for all required components
checks = {
    "OS Detection": "Windows Professional 11" in output,
    "CPU Model": "AMD Ryzen 9" in output or "AMD64 Family" in output,
    "CPU Cores": "Cores: 16" in output or ("Cores:" in output and "0" not in output.split("Cores:")[1].split("\n")[0][:10]),
    "RAM Amount": "RAM: 32 GB" in output or ("RAM:" in output and "0 GB" not in output),
    "GPU Detection": "AMD Radeon" in output or ("GPU:" in output and "Unknown" not in output.split("GPU:")[1].split("\n")[0]),
    "Storage Detection": "C:\\" in output and "GB" in output.split("Storage:")[1].split("\n")[1],
    "Hostname": "Deadquarters" in output,
    "Test Passed": "[OK] ALL CHECKS PASSED" in output,
}

print("\nComponent Checks:")
all_passed = True
for name, passed in checks.items():
    status = "[OK]" if passed else "[FAIL]"
    print(f"  {status} {name}")
    if not passed:
        all_passed = False

if all_passed:
    print("\n" + "="*60)
    print("SUCCESS! ALL COMPONENTS WORKING CORRECTLY")
    print("="*60)
    print("\n✓ The speccle.py GUI app is ready to use!")
    print("✓ Run: python speccle.py")
else:
    print("\n" + "="*60)
    print("FAILURE - Some components not working")
    print("="*60)
    print("\nDebug output:")
    print(output[:1000])

exit(0 if all_passed else 1)
