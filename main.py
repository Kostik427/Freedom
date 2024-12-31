import ctypes
import os
import sys
from typing import List

def is_admin() -> bool:
    """Check if the script is running with administrative privileges.

    Returns:
        bool: True if the script is running as an admin, False otherwise.
    
    
    
    """
    if os.name == 'nt':  # Windows
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False
    else:  # Linux/Unix
        return os.geteuid() == 0

def is_ipv6_enabled() -> bool:
    """Check if IPv6 is enabled in the system.

    Returns:
        bool: True if IPv6 is enabled, False otherwise.
    """
    if os.name == 'nt':  # Windows
        return True  # Simplified assumption for Windows
    else:  # Linux
        try:
            with open('/proc/sys/net/ipv6/conf/all/disable_ipv6', 'r') as f:
                return f.read().strip() == '0'
        except FileNotFoundError:
            return True

def extract_ips_from_static_hosts(filename: str) -> None:
    """Extract IPs from a file and append them to the system hosts file.

    Args:
        filename (str): The path to the file containing host entries.
    """
    if not is_admin():
        print("This script requires administrative privileges.")
        if os.name == 'nt':
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit(1)

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines: List[str] = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Unable to read file '{filename}': {e}")
        sys.exit(1)

    host_file_path: str = (
        'C:/Windows/System32/drivers/etc/hosts' if os.name == 'nt' else '/etc/hosts'
    )

    try:
        with open(host_file_path, 'a+', encoding='utf-8') as f:
            f.seek(0)
            host_lines: List[str] = f.readlines()
            existing_hosts: set[str] = {
                line.split()[1] for line in host_lines if len(line.split()) > 1
            }

            for hostname in lines:
                if hostname not in existing_hosts:
                    f.write(f'127.0.0.1 {hostname}\n')
                    f.write(f'127.0.1.1 {hostname}\n')
                    f.write(f'::1 {hostname}\n')
                    if os.name != 'nt':
                        f.write(f'127.0.1.1 {hostname}\n')
                        f.write(f'127.0.0.1 {hostname}\n')
                        if is_ipv6_enabled():
                            f.write(f'::1 {hostname}\n')
    except PermissionError:
        print(f"Error: Permission denied when trying to write to '{host_file_path}'.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Unable to update '{host_file_path}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    extract_ips_from_static_hosts('static_hosts.txt')
    print("Done")
    input("Press Enter to exit...")
