# Domain and IP Address Management Tools (FREEDOM)

This toolkit is designed for working with domains and IP addresses associated with specific services. The tools allow for IP address extraction from domains, reverse IP lookups, and hosts file management.

## Project Structure

The project consists of the following scripts:

1. `extract_ips.py` - extracts IP addresses from a list of domains
2. `reverse_ips.py` / `reverse_ips.go` - performs reverse IP lookups
3. `freedom.py` - manages hosts file entries

## Detailed Component Description

### extract_ips.py

This script is designed to extract IP addresses from a list of domains.

**Functionality:**
- Reads domain list from `ru_services.txt`
- Pings each domain to obtain its IP address
- Saves unique IP addresses to `iptables.txt`

**Usage:**
```bash
python extract_ips.py
```

### reverse_ips.py / reverse_ips.go

Scripts for performing reverse IP lookups. Available in both Python and Go versions.

**Functionality:**
- Uses HackerTarget API for domain lookups
- Optional SecurityTrails API integration (requires API key)
- Asynchronous request processing
- Saves results to `domains_found.txt`

**Setup:**
1. Create `iptables.txt` with a list of IP addresses
2. Obtain SecurityTrails API key if needed
3. Set the API key in `security_trails_api_key` variable

**Python version usage:**
```bash
python reverse_ips.py
```

**Go version usage:**
```bash
go run reverse_ips.go
```

### freedom.py

Script for managing system hosts file entries.

**Functionality:**
- Adds entries to hosts file to redirect domains to localhost
- Requires administrator privileges
- Automatic privilege elevation request

**Usage:**
1. Create `static_hots.txt` with a list of domains
2. Run the script:
```bash
python freedom.py
```

## Requirements

- Python 3.7+
- Go 1.15+ (for Go version)
- Python libraries: aiohttp, asyncio
- Internet access for API requests
- Administrator privileges (for freedom.py)

## Security Notes

- Scripts modify system files - use with caution
- Keep API keys secure
- Verify domains before adding to hosts file

## File Flow

1. Start with `ru_services.txt` containing target domains
2. Run `extract_ips.py` to generate `iptables.txt`
3. Use `reverse_ips.py` or `reverse_ips.go` to generate `domains_found.txt`
4. Create `static_hots.txt` from discovered domains
5. Use `freedom.py` to update system hosts file

## API Keys

To use SecurityTrails API:
1. Register at securitytrails.com
2. Obtain API key
3. Replace `YOUR_API_KEY` in the scripts with your actual key

Remember to respect API rate limits and terms of service.
