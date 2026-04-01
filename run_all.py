import threading
import subprocess
import os

# Diretórios e portas de cada serviço
services = [
    {"name": "msa", "path": "msa/manage.py", "port": 8001},
    {"name": "msb", "path": "msb/manage.py", "port": 8002},
    {"name": "msc", "path": "msc/manage.py", "port": 8003},
    {"name": "sidecar_a", "path": "sidecar_a/manage.py", "port": 9001},
    {"name": "sidecar_b", "path": "sidecar_b/manage.py", "port": 9002},
    {"name": "sidecar_c", "path": "sidecar_c/manage.py", "port": 9003},
]

# Cria pasta de logs
os.makedirs("logs", exist_ok=True)

def run_service(service):
    log_file = f"logs/{service['name']}.log"
    cmd = f"python {service['path']} runserver {service['port']}"
    print(f"[START] {service['name']} -> {cmd}")
    with open(log_file, "w") as f:
        process = subprocess.Popen(cmd, shell=True, stdout=f, stderr=f)
        process.wait()  # aguarda o serviço terminar (Ctrl+C para parar todos)

threads = []
for svc in services:
    t = threading.Thread(target=run_service, args=(svc,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()
