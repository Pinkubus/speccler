"""
Speccle - System Specification Detector
A lightweight desktop utility that detects and displays hardware/OS specifications.
"""

import platform
import socket
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os

# Cross-platform imports with fallbacks
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Windows-specific imports
try:
    import wmi
    import pythoncom
    HAS_WMI = True
except ImportError:
    HAS_WMI = False


class SystemInfoCollector:
    """Collects system hardware and OS specifications."""
    
    def __init__(self):
        self.specs = {}
    
    def collect_all(self) -> dict:
        """Collect all system specifications."""
        # Initialize COM for WMI on Windows (required for threading)
        if HAS_WMI and platform.system() == 'Windows':
            try:
                pythoncom.CoInitialize()
            except:
                pass  # Already initialized
        
        try:
            self.specs = {
                'os': self._get_os_info(),
                'cpu': self._get_cpu_info(),
                'ram': self._get_ram_info(),
                'gpu': self._get_gpu_info(),
                'storage': self._get_storage_info(),
                'motherboard': self._get_motherboard_info(),
                'system': self._get_system_info(),
            }
        finally:
            if HAS_WMI and platform.system() == 'Windows':
                try:
                    pythoncom.CoUninitialize()
                except:
                    pass
        
        return self.specs
    
    def _get_os_info(self) -> dict:
        """Get operating system information."""
        info = {
            'name': platform.system(),
            'version': platform.version(),
            'release': platform.release(),
            'architecture': platform.machine(),
        }
        
        # Windows-specific details
        if platform.system() == 'Windows':
            try:
                info['edition'] = platform.win32_edition()
            except:
                info['edition'] = ''
            
            # Get build number from version
            version_parts = platform.version().split('.')
            if len(version_parts) >= 3:
                info['build'] = version_parts[2]
        
        return info
    
    def _get_cpu_info(self) -> dict:
        """Get CPU information."""
        info = {
            'model': platform.processor() or 'Unknown',
            'physical_cores': 0,
            'logical_cores': 0,
            'frequency': None,
            'manufacturer': '',
        }
        
        if HAS_PSUTIL:
            try:
                info['physical_cores'] = psutil.cpu_count(logical=False) or 0
                info['logical_cores'] = psutil.cpu_count(logical=True) or 0
            except:
                pass
            
            try:
                freq = psutil.cpu_freq()
                if freq:
                    info['frequency'] = freq.max or freq.current
            except:
                pass
        
        # Windows WMI for detailed CPU info
        if HAS_WMI and platform.system() == 'Windows':
            try:
                c = wmi.WMI()
                for cpu in c.Win32_Processor():
                    info['model'] = cpu.Name.strip() if cpu.Name else info['model']
                    info['manufacturer'] = cpu.Manufacturer or ''
                    if cpu.MaxClockSpeed:
                        info['frequency'] = cpu.MaxClockSpeed
                    # Get cores from WMI if not already set
                    if info['physical_cores'] == 0 and cpu.NumberOfCores:
                        info['physical_cores'] = cpu.NumberOfCores
                    if info['logical_cores'] == 0 and cpu.NumberOfLogicalProcessors:
                        info['logical_cores'] = cpu.NumberOfLogicalProcessors
                    break
            except:
                pass
        
        # Fallback to os.cpu_count() if still no data
        if info['logical_cores'] == 0:
            import os
            info['logical_cores'] = os.cpu_count() or 0
            if info['physical_cores'] == 0:
                # Assume physical cores is half of logical (common for hyperthreading)
                info['physical_cores'] = info['logical_cores'] // 2 if info['logical_cores'] > 1 else info['logical_cores']
        
        return info
    
    def _get_ram_info(self) -> dict:
        """Get RAM information."""
        info = {
            'total': 0,
            'available': 0,
        }
        
        if HAS_PSUTIL:
            try:
                mem = psutil.virtual_memory()
                info['total'] = mem.total
                info['available'] = mem.available
            except:
                pass
        
        # Windows WMI fallback for RAM
        if info['total'] == 0 and HAS_WMI and platform.system() == 'Windows':
            try:
                c = wmi.WMI()
                for os_info in c.Win32_OperatingSystem():
                    if os_info.TotalVisibleMemorySize:
                        info['total'] = int(os_info.TotalVisibleMemorySize) * 1024  # Convert KB to bytes
                    if os_info.FreePhysicalMemory:
                        info['available'] = int(os_info.FreePhysicalMemory) * 1024
                    break
            except:
                pass
        
        return info
    
    def _get_gpu_info(self) -> list:
        """Get GPU information."""
        gpus = []
        
        # Windows WMI
        if HAS_WMI and platform.system() == 'Windows':
            try:
                c = wmi.WMI()
                for gpu in c.Win32_VideoController():
                    # Only add real GPUs (skip Microsoft Basic Display Adapter)
                    if gpu.Name and 'Basic Display' not in gpu.Name and 'Basic Render' not in gpu.Name:
                        # Handle VRAM - some GPUs report negative values or None
                        vram = 0
                        if gpu.AdapterRAM and gpu.AdapterRAM > 0:
                            vram = gpu.AdapterRAM
                        
                        gpu_info = {
                            'name': gpu.Name or 'Unknown GPU',
                            'vendor': gpu.AdapterCompatibility or '',
                            'vram': vram,
                        }
                        gpus.append(gpu_info)
            except Exception as e:
                # If WMI fails completely, will use fallback below
                pass
        
        # Fallback for non-Windows or if WMI fails
        if not gpus:
            gpus.append({
                'name': 'Unknown GPU',
                'vendor': '',
                'vram': 0,
            })
        
        return gpus
    
    def _get_storage_info(self) -> list:
        """Get storage drive information."""
        drives = []
        
        if HAS_PSUTIL:
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    # Skip CD-ROMs and network drives
                    if 'cdrom' in partition.opts.lower() or partition.fstype == '':
                        continue
                    
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    drive_info = {
                        'mount': partition.mountpoint,
                        'device': partition.device,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'free': usage.free,
                        'type': 'Unknown',
                    }
                    
                    drives.append(drive_info)
                except (PermissionError, OSError):
                    continue
        
        # Windows WMI for drive type detection
        if HAS_WMI and platform.system() == 'Windows':
            try:
                c = wmi.WMI()
                # Get physical disk info
                disk_types = {}
                for disk in c.Win32_DiskDrive():
                    media_type = 'Unknown'
                    if disk.MediaType:
                        if 'SSD' in disk.MediaType or 'Solid' in disk.MediaType.upper():
                            media_type = 'SSD'
                        elif 'Fixed' in disk.MediaType:
                            # Check interface for NVMe
                            if disk.InterfaceType and 'NVMe' in disk.InterfaceType:
                                media_type = 'NVMe SSD'
                            else:
                                media_type = 'HDD'
                    disk_types[disk.Index] = media_type
                
                # Match partitions to physical disks
                for partition in c.Win32_DiskDriveToDiskPartition():
                    disk_index = int(partition.Antecedent.split('Disk #')[1].split(',')[0])
                    part_index = partition.Dependent.split('Partition #')[1].strip('"')
                    
                    for logical in c.Win32_LogicalDiskToPartition():
                        if f'Partition #{part_index}' in logical.Antecedent:
                            drive_letter = logical.Dependent.split('=')[1].strip('"')
                            for drive in drives:
                                if drive_letter in drive['mount']:
                                    drive['type'] = disk_types.get(disk_index, 'Unknown')
            except:
                pass
        
        return drives
    
    def _get_motherboard_info(self) -> dict:
        """Get motherboard information."""
        info = {
            'manufacturer': 'Unknown',
            'model': 'Unknown',
        }
        
        if HAS_WMI and platform.system() == 'Windows':
            try:
                c = wmi.WMI()
                for board in c.Win32_BaseBoard():
                    info['manufacturer'] = board.Manufacturer or 'Unknown'
                    info['model'] = board.Product or 'Unknown'
                    break
            except:
                pass
        
        return info
    
    def _get_system_info(self) -> dict:
        """Get system identifiers."""
        return {
            'hostname': socket.gethostname(),
            'architecture': platform.machine(),
        }
    
    def format_output(self) -> str:
        """Format all collected specs as human-readable text."""
        if not self.specs:
            self.collect_all()
        
        lines = []
        
        # OS Section
        os_info = self.specs['os']
        os_name = os_info['name']
        if os_info.get('edition'):
            os_name += f" {os_info['edition']}"
        os_name += f" {os_info['release']}"
        if os_info.get('build'):
            os_name += f" (Build {os_info['build']})"
        
        lines.append(f"OS: {os_name}")
        lines.append(f"Architecture: {os_info['architecture']}")
        lines.append("")
        
        # CPU Section
        cpu = self.specs['cpu']
        lines.append(f"CPU: {cpu['model']}")
        cores_str = f"Cores: {cpu['physical_cores']} / Threads: {cpu['logical_cores']}"
        if cpu['frequency']:
            freq_ghz = cpu['frequency'] / 1000 if cpu['frequency'] > 1000 else cpu['frequency']
            if freq_ghz > 100:  # Still in MHz
                freq_ghz = freq_ghz / 1000
            cores_str += f" @ {freq_ghz:.2f} GHz"
        lines.append(cores_str)
        lines.append("")
        
        # RAM Section
        ram = self.specs['ram']
        total_gb = ram['total'] / (1024 ** 3)
        lines.append(f"RAM: {total_gb:.0f} GB")
        if ram['available']:
            avail_gb = ram['available'] / (1024 ** 3)
            lines.append(f"     ({avail_gb:.1f} GB available)")
        lines.append("")
        
        # GPU Section
        for i, gpu in enumerate(self.specs['gpu']):
            gpu_str = f"GPU: {gpu['name']}"
            if gpu['vram'] and gpu['vram'] > 0:
                vram_gb = gpu['vram'] / (1024 ** 3)
                if vram_gb >= 1:
                    gpu_str += f" ({vram_gb:.0f} GB VRAM)"
                else:
                    vram_mb = gpu['vram'] / (1024 ** 2)
                    gpu_str += f" ({vram_mb:.0f} MB VRAM)"
            lines.append(gpu_str)
        lines.append("")
        
        # Storage Section
        lines.append("Storage:")
        for drive in self.specs['storage']:
            total_gb = drive['total'] / (1024 ** 3)
            free_gb = drive['free'] / (1024 ** 3)
            
            # Format size appropriately
            if total_gb >= 1000:
                total_str = f"{total_gb / 1024:.1f} TB"
                free_str = f"{free_gb / 1024:.2f} TB" if free_gb >= 1000 else f"{free_gb:.0f} GB"
            else:
                total_str = f"{total_gb:.0f} GB"
                free_str = f"{free_gb:.0f} GB"
            
            drive_type = drive['type'] if drive['type'] != 'Unknown' else ''
            if drive_type:
                lines.append(f"  - {drive['mount']} {drive_type} – {total_str} ({free_str} free)")
            else:
                lines.append(f"  - {drive['mount']} {total_str} ({free_str} free)")
        lines.append("")
        
        # Motherboard Section
        mb = self.specs['motherboard']
        if mb['manufacturer'] != 'Unknown' or mb['model'] != 'Unknown':
            mb_str = f"{mb['manufacturer']} {mb['model']}".strip()
            lines.append(f"Motherboard: {mb_str}")
        
        # System Section
        sys_info = self.specs['system']
        lines.append(f"Hostname: {sys_info['hostname']}")
        
        return '\n'.join(lines)


class SpeccleApp:
    """Main application window."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Speccle - System Specs")
        self.root.geometry("600x500")
        self.root.minsize(400, 300)
        
        # Set icon if available (optional)
        try:
            self.root.iconbitmap(default='')
        except:
            pass
        
        self._setup_ui()
        self._load_specs()
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Text area with scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=0, column=0, sticky="nsew")
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        
        self.text_area = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Consolas", 11),
            padx=10,
            pady=10,
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground="#cccccc",
            highlightcolor="#0078d4",
        )
        self.text_area.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_area.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text_area.configure(yscrollcommand=scrollbar.set)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, pady=(10, 0), sticky="e")
        
        # Copy button
        self.copy_button = ttk.Button(
            button_frame,
            text="📋 Copy to Clipboard",
            command=self._copy_to_clipboard,
            width=20,
        )
        self.copy_button.grid(row=0, column=0)
        
        # Status label
        self.status_label = ttk.Label(button_frame, text="", foreground="green")
        self.status_label.grid(row=0, column=1, padx=(10, 0))
    
    def _load_specs(self):
        """Load system specs in a background thread."""
        self.text_area.insert(tk.END, "Detecting system specifications...")
        self.text_area.configure(state=tk.DISABLED)
        
        def collect():
            collector = SystemInfoCollector()
            specs_text = collector.format_output()
            self.root.after(0, lambda: self._display_specs(specs_text))
        
        thread = threading.Thread(target=collect, daemon=True)
        thread.start()
    
    def _display_specs(self, specs_text: str):
        """Display the collected specs in the text area."""
        self.text_area.configure(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, specs_text)
        # Keep text selectable but not editable
        self.text_area.configure(state=tk.DISABLED)
    
    def _copy_to_clipboard(self):
        """Copy all text to clipboard."""
        # Temporarily enable to get text
        self.text_area.configure(state=tk.NORMAL)
        text = self.text_area.get(1.0, tk.END).strip()
        self.text_area.configure(state=tk.DISABLED)
        
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        
        # Show confirmation
        self.status_label.configure(text="✓ Copied!")
        self.root.after(2000, lambda: self.status_label.configure(text=""))
    
    def run(self):
        """Start the application."""
        self.root.mainloop()


def main():
    """Application entry point."""
    app = SpeccleApp()
    app.run()


if __name__ == "__main__":
    main()
