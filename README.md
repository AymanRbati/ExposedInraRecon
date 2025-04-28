# ExposedInfraRecon

**ExposedInfraRecon** is a lightweight Python 3 tool designed for fast reconnaissance of internet-exposed infrastructure.

It automates:
- Collecting subdomains from crt.sh
- Resolving subdomains into both IPv4 and IPv6 addresses
- Fast full-port scanning of resolved IPs with parallel Nmap
- Organizing results into clean output files for triage


---

## ✨ Features

- ✅ Fetch subdomains from crt.sh per domain
- ✅ Resolve both IPv4 (A records) and IPv6 (AAAA records)
- ✅ Save all subdomains into `subdomains.txt`
- ✅ Save all unique IPs into `IPs.txt`
- ✅ Fast full-port Nmap scanning (`-p-`, ports 1–65535) with parallel threading
- ✅ Scan IPv4 and IPv6 correctly
- ✅ Save all scan results into `nmap.txt`
- ✅ Error handling and live status updates

---

## 🚀 Installation

```bash
git clone https://github.com/yourusername/ExposedInfraRecon.git
cd ExposedInfraRecon
pip install requests
sudo apt install nmap -y
