"""Debug script to test system detection and fix issues."""

import platform
import socket
import sys
import traceback

# Cross-platform imports with fallbacks
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("WARNING: psutil not available")

# Windows-specific imports
try:
    import wmi
    import pythoncom
    HAS_WMI = True
except ImportError:
    HAS_WMI = False
    print("WARNING: WMI not available")

def test_ram():
    """Test RAM detection."""
    print("\n=== Testing RAM Detection ===")
    
    if HAS_PSUTIL:
        try:
            mem = psutil.virtual_memory()
            total_gb = mem.total / (1024 ** 3)
            avail_gb = mem.available / (1024 ** 3)
            print(f"✓ psutil: {total_gb:.2f} GB total, {avail_gb:.2f} GB available")
            return True
        except Exception as e:
            print(f"✗ psutil failed: {e}")
            traceback.print_exc()
    
    if HAS_WMI and platform.system() == 'Windows':
        try:
            pythoncom.CoInitialize()
            c = wmi.WMI()
            for os_info in c.Win32_OperatingSystem():
                if os_info.TotalVisibleMemorySize:
                    total = int(os_info.TotalVisibleMemorySize) * 1024
                    total_gb = total / (1024 ** 3)
                    print(f"✓ WMI: {total_gb:.2f} GB total")
                    return True
                break
        except Exception as e:
            print(f"✗ WMI failed: {e}")
            traceback.print_exc()
        finally:
            try:
                pythoncom.CoUninitialize()
            except:
                pass
    
    return False

def test_gpu():
    """Test GPU detection."""
    print("\n=== Testing GPU Detection ===")
    
    if HAS_WMI and platform.system() == 'Windows':
        try:
            pythoncom.CoInitialize()
            c = wmi.WMI()
            found_gpu = False
            for gpu in c.Win32_VideoController():
                print(f"Found: {gpu.Name}")
                print(f"  Vendor: {gpu.AdapterCompatibility}")
                print(f"  VRAM: {gpu.AdapterRAM}")
                if gpu.Name and 'Basic Display' not in gpu.Name:
                    found_gpu = True
            
            if found_gpu:
                print("✓ WMI GPU detection working")
                return True
            else:
                print("✗ No valid GPU found")
                
        except Exception as e:
            print(f"✗ WMI failed: {e}")
            traceback.print_exc()
        finally:
            try:
                pythoncom.CoUninitialize()
            except:
                pass
    
    return False

def test_storage():
    """Test storage detection."""
    print("\n=== Testing Storage Detection ===")
    
    if HAS_PSUTIL:
        try:
            partitions = psutil.disk_partitions()
            print(f"Found {len(partitions)} partitions:")
            for p in partitions:
                print(f"  {p.device} -> {p.mountpoint} ({p.fstype})")
                try:
                    usage = psutil.disk_usage(p.mountpoint)
                    total_gb = usage.total / (1024 ** 3)
                    print(f"    {total_gb:.2f} GB total")
                except Exception as e:
                    print(f"    Error getting usage: {e}")
            return len(partitions) > 0
        except Exception as e:
            print(f"✗ psutil failed: {e}")
            traceback.print_exc()
    
    return False

def main():
    print("System Detection Debug Tool")
    print("=" * 50)
    print(f"Python: {sys.version}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"HAS_PSUTIL: {HAS_PSUTIL}")
    print(f"HAS_WMI: {HAS_WMI}")
    
    results = {
        'RAM': test_ram(),
        'GPU': test_gpu(),
        'Storage': test_storage(),
    }
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    for component, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {component}: {status}")
    
    all_pass = all(results.values())
    print("\n" + "=" * 50)
    if all_pass:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED - needs fixing")
    
    return all_pass

if __name__ == "__main__":
    main()
