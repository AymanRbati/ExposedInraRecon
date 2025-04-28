#!/usr/bin/env python3

import socket
import requests
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

def fetch_subdomains(domain):
    print(f"[*] Fetching subdomains for: {domain}")
    subdomains = set()
    try:
        response = requests.get(f"https://crt.sh/?q=%25.{domain}&output=json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            for entry in data:
                for name in entry['name_value'].split("\n"):
                    subdomains.add(name.replace("*.", "").strip())
        else:
            print(f"[!] Failed to fetch crt.sh data for {domain}")
    except Exception as e:
        print(f"[!] Error fetching crt.sh for {domain}: {e}")
    return subdomains

def resolve_subdomain(subdomain):
    results = []
    try:
        ipv4 = socket.gethostbyname(subdomain)
        print(f"[IPv4] {subdomain} -> {ipv4}")
        results.append(ipv4)
    except Exception:
        pass
    try:
        info = socket.getaddrinfo(subdomain, None, socket.AF_INET6)
        for entry in info:
            ipv6 = entry[4][0]
            print(f"[IPv6] {subdomain} -> {ipv6}")
            results.append(ipv6)
    except Exception:
        pass
    return results

def nmap_scan(ip):
    try:
        if ":" in ip:
            # IPv6
            print(f"[*] Scanning IPv6: {ip}")
            result = subprocess.run(
                [
                    "nmap", "-6", "-Pn", "-p-", "--min-rate", "5000", "--max-retries", "2",
                    "--open", "--disable-arp-ping", ip
                ],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
        else:
            # IPv4
            print(f"[*] Scanning IPv4: {ip}")
            result = subprocess.run(
                [
                    "nmap", "-Pn", "-p-", "--min-rate", "5000", "--max-retries", "2",
                    "--open", "--disable-arp-ping", ip
                ],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
        with open("nmap.txt", "a") as nmap_out:
            nmap_out.write(result.stdout.decode() + "\n")
    except Exception as e:
        print(f"[!] Error scanning {ip}: {e}")

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} domains.txt")
    sys.exit(1)

domains_file = sys.argv[1]

try:
    with open(domains_file, 'r') as f:
        domains = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print(f"[!] File {domains_file} not found.")
    sys.exit(1)

# Clean output files
open('subdomains.txt', 'w').close()
open('IPs.txt', 'w').close()
open('nmap.txt', 'w').close()

all_subdomains = set()
all_ips = set()

print(f"[*] Starting FULL Recon for domains in: {domains_file}")

# Step 1: Fetch subdomains
for domain in domains:
    subs = fetch_subdomains(domain)
    all_subdomains.update(subs)

# Save subdomains
with open('subdomains.txt', 'w') as subfile:
    for sub in sorted(all_subdomains):
        subfile.write(sub + "\n")

print(f"\n[*] Total subdomains collected: {len(all_subdomains)}")

# Step 2: Resolve subdomains
print(f"\n[*] Resolving subdomains...")
with ThreadPoolExecutor(max_workers=30) as executor:
    results = executor.map(resolve_subdomain, all_subdomains)

for ips in results:
    for ip in ips:
        all_ips.add(ip)

# Save IPs
with open('IPs.txt', 'w') as ipfile:
    for ip in sorted(all_ips):
        ipfile.write(ip + "\n")

print(f"\n[*] Total unique IPs collected: {len(all_ips)}")

if not all_ips:
    print("[!] No IPs resolved. Exiting.")
    sys.exit(1)

# Step 3: Parallel Nmap scan (FAST)
print("\n[*] Launching fast parallel Nmap scans (full port range)...")
with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(nmap_scan, all_ips)

print("\n[*] Full Recon and Fast Scan complete.")
print("[*] Subdomains saved in: subdomains.txt")
print("[*] IPs saved in: IPs.txt")
print("[*] Nmap results saved in: nmap.txt")
