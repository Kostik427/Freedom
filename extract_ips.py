import os
import subprocess
from typing import List, Set

def read_domains(file_path: str) -> List[str]:
    """Reads domain names from a file.

    Args:
        file_path (str): Path to the file containing domain names.

    Returns:
        List[str]: A list of domain names.
    
    """
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден. Создайте его и добавьте список доменов.")
        exit(1)

    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def ping_domain(domain: str) -> str:
    """Pings a domain and extracts its IP address.

    Args:
        domain (str): The domain name to ping.

    Returns:
        str: The IP address of the domain, or an empty string if ping fails.
    """
    try:
        print(f"Пингуем {domain}...")
        result = subprocess.run(["ping", "-c", "1", domain], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.splitlines()
            for line in lines:
                if "PING" in line:
                    start = line.find("(") + 1
                    end = line.find(")")
                    if start > 0 and end > start:
                        ip = line[start:end]
                        print(f"Найден IP: {ip}")
                        return ip
        else:
            print(f"Ошибка пинга для {domain}: {result.stderr.strip()}")
    except Exception as e:
        print(f"Ошибка обработки домена {domain}: {e}")
    return ""

def extract_unique_ips(domains: List[str]) -> Set[str]:
    """Extracts unique IP addresses from a list of domains.

    Args:
        domains (List[str]): A list of domain names.

    Returns:
        Set[str]: A set of unique IP addresses.
    """
    unique_ips: Set[str] = set()
    for domain in domains:
        ip = ping_domain(domain)
        if ip:
            unique_ips.add(ip)
    return unique_ips

def write_ips_to_file(ips: Set[str], file_path: str) -> None:
    """Writes unique IP addresses to a file.

    Args:
        ips (Set[str]): A set of unique IP addresses.
        file_path (str): The file path to write the IPs to.
    """
    with open(file_path, "w") as f:
        for ip in sorted(ips):
            f.write(ip + "\n")
    print(f"Уникальные IP-адреса сохранены в {file_path}.")

def main() -> None:
    """Main function to read domains, extract IPs, and write them to a file."""
    input_file = "ru_services.txt"
    output_file = "iptables.txt"

    domains = read_domains(input_file)
    unique_ips = extract_unique_ips(domains)
    write_ips_to_file(unique_ips, output_file)

if __name__ == "__main__":
    main()