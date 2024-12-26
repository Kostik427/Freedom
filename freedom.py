import ctypes
import sys
from typing import List

def is_admin() -> bool:
    """Check if the script is running with administrative privileges.

    Returns:
        bool: True if the script is running as an admin, False otherwise.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def extract_ips_from_static_hots(filename: str) -> None:
    """Extract IPs from a file and append them to the hosts file.

    Args:
        filename (str): The path to the file containing host entries.
    """
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

    with open(filename, 'r') as file:
        lines: List[str] = file.readlines()
    
    for index, line in enumerate(lines):
        if index % 2 != 0:
            with open('C:/Windows/System32/drivers/etc/hosts', 'a+') as f:
                f.seek(0)
                host_lines: List[str] = f.readlines()
                existing_hosts: List[str] = [l.split()[1] for l in host_lines if len(l.split()) > 1]
                if line.strip() not in existing_hosts:
                    f.write('127.0.0.1 ' + line.strip() + '\n')

extract_ips_from_static_hots('static_hots.txt')

print("Done")
input("Press Enter to exit...")

