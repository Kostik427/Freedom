import asyncio
import aiohttp
from typing import List, Set


class ReverseIPLookup:
    """Reverse IP lookup using multiple services"""

    def __init__(self) -> None:
        """Initialize the ReverseIPLookup object"""
        self.unique_domains: Set[str] = set()

    async def get_domains_hackertarget(self, ip: str, session: aiohttp.ClientSession) -> List[str]:
        """Using HackerTarget API to get reverse IP data

        Args:
            ip (str): IP address to look up
            session (aiohttp.ClientSession): Session to use for the request

        Returns:
            List[str]: List of domains found for the given IP
        """
        url = f"https://api.hackertarget.com/reverseiplookup/?q={ip}"
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    text = await response.text()
                    return [domain.strip() for domain in text.split('\n') if domain.strip()]
                return []
        except Exception as e:
            print(f"Error with HackerTarget API: {e}")
            return []

    async def get_domains_securitytrails(self, ip: str, session: aiohttp.ClientSession, api_key: str) -> List[str]:
        """Using SecurityTrails API to get reverse IP data

        Args:
            ip (str): IP address to look up
            session (aiohttp.ClientSession): Session to use for the request
            api_key (str): SecurityTrails API key

        Returns:
            List[str]: List of domains found for the given IP
        """
        url = f"https://api.securitytrails.com/v1/ips/{ip}/domains"
        headers = {"apikey": api_key}
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('domains', [])
                return []
        except Exception as e:
            print(f"Error with SecurityTrails API: {e}")
            return []

    async def process_ip(self, ip: str, session: aiohttp.ClientSession, security_trails_api_key: str = None) -> Set[str]:
        """Process single IP address using multiple services

        Args:
            ip (str): IP address to look up
            session (aiohttp.ClientSession): Session to use for the request
            security_trails_api_key (str, optional): SecurityTrails API key. Defaults to None.

        Returns:
            Set[str]: Set of unique domains found for the given IP
        """
        print(f"Processing IP: {ip}")
        domains = set()

        # Get domains from HackerTarget
        ht_domains = await self.get_domains_hackertarget(ip, session)
        domains.update(ht_domains)

        # If SecurityTrails API key is provided, use it as well
        if security_trails_api_key:
            st_domains = await self.get_domains_securitytrails(ip, session, security_trails_api_key)
            domains.update(st_domains)

        self.unique_domains.update(domains)
        return domains

    async def process_ips(self, ips: List[str], security_trails_api_key: str = None) -> None:
        """Process multiple IP addresses concurrently

        Args:
            ips (List[str]): List of IP addresses to look up
            security_trails_api_key (str, optional): SecurityTrails API key. Defaults to None.
        """
        async with aiohttp.ClientSession() as session:
            tasks = []
            for ip in ips:
                # Add delay between requests to avoid rate limiting
                await asyncio.sleep(1)
                tasks.append(self.process_ip(ip, session, security_trails_api_key))
            await asyncio.gather(*tasks)

    def save_results(self, output_file: str) -> None:
        """Save results to file

        Args:
            output_file (str): File to save the results to
        """
        with open(output_file, 'w') as f:
            for domain in sorted(self.unique_domains):
                f.write(f"{domain}\n")
        print(f"Results saved to {output_file}")

async def main() -> None:
    """Main function to run the script"""
    input_file = "iptables.txt"
    output_file = "domains_found.txt"
    security_trails_api_key = "YOUR_API_KEY"

    with open(input_file, 'r') as f:
        ips = [line.strip() for line in f if line.strip()]

    lookup = ReverseIPLookup()
    await lookup.process_ips(ips, security_trails_api_key)
    lookup.save_results(output_file)

if __name__ == "__main__":
    asyncio.run(main())
