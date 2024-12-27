import os
import sys
from typing import List

def is_admin() -> bool:
    """Check if the script is running with administrative privileges.

    Returns:
        bool: True if the script is running as an admin, False otherwise.
    """
    return os.geteuid() == 0


def is_ipv6_enabled() -> bool:
    """Check if IPv6 is enabled in the system."""
    try:
        with open('/proc/sys/net/ipv6/conf/all/disable_ipv6', 'r') as f:
            return f.read().strip() == '0'
    except FileNotFoundError:
        # Если файл не существует, считаем, что IPv6 включён
        return True

def extract_ips_from_static_hots(filename: str) -> None:
    """Extract IPs from a file and append them to the hosts file.

    Args:
        filename (str): The path to the file containing host entries.
    """
    if not is_admin():
        print("This script requires administrative privileges.")
        sys.exit(1)

    with open(filename, 'r') as file:
        lines: List[str] = file.readlines()
    
    with open('/etc/hosts', 'a+') as f:
        f.seek(0)
        host_lines: List[str] = f.readlines()
        existing_hosts: List[str] = [l.split()[1] for l in host_lines if len(l.split()) > 1]
        for index, line in enumerate(lines):
            if index % 2 != 0 and line.strip() not in existing_hosts:
                f.write('127.0.0.1 ' + line.strip() + '\n')
                f.write('127.0.1.1 ' + line.strip() + '\n')
                if is_ipv6_enabled() == True:
                    f.write('::1 ' + line.strip() + '\n')
                    f.write('fe00::0 ' + line.strip() + '\n')
                    f.write('ff02::1 ' + line.strip() + '\n')
                    f.write('ff02::2 ' + line.strip() + '\n')
                    
                else:
                    print('i cant enable ipv6')
                    return

extract_ips_from_static_hots('static_hots.txt')

print("Done")
input("Press Enter to exit...")

