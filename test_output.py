"""Test script to verify output without GUI."""

import sys
sys.path.insert(0, '.')

from speccle import SystemInfoCollector

def main():
    print("Collecting system specifications...")
    collector = SystemInfoCollector()
    output = collector.format_output()
    print("\n" + "="*60)
    print(output)
    print("="*60)
    
    # Check for failures
    failures = []
    if "0 GB" in output and "RAM: 0 GB" in output:
        failures.append("RAM shows 0 GB")
    if "Unknown GPU" in output and "AMD" not in output and "NVIDIA" not in output and "Intel" not in output:
        failures.append("GPU not detected properly")
    if "Storage:\n\n" in output or "Storage:\n\nMotherboard" in output or "Storage:\n\nHostname" in output:
        failures.append("No storage drives detected")
    if "Cores: 0" in output:
        failures.append("CPU cores show 0")
    
    if failures:
        print("\n[X] FAILURES DETECTED:")
        for f in failures:
            print(f"  - {f}")
        return False
    else:
        print("\n[OK] ALL CHECKS PASSED!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
