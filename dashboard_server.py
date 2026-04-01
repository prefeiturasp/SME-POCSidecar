import subprocess
import os
import signal
import time
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import httpx
import re

# Configuração dos serviços
SERVICES = {
    "msa": {"path": "msa/manage.py", "port": 8001, "proc": None},
    "msb": {"path": "msb/manage.py", "port": 8002, "proc": None},
    "msc": {"path": "msc/manage.py", "port": 8003, "proc": None},
    "sidecar_a": {"path": "sidecar_a/manage.py", "port": 9001, "proc": None},
    "sidecar_b": {"path": "sidecar_b/manage.py", "port": 9002, "proc": None},
    "sidecar_c": {"path": "sidecar_c/manage.py", "port": 9003, "proc": None},
}

LOGS = []
SYSTEM_LOGS = LOGS

def is_port_open(port):
    res = subprocess.run(f"netstat -ano | findstr :{port}", shell=True, capture_output=True)
    return "LISTENING" in res.stdout.decode()

def log(msg):
    LOGS.append(f"[{time.strftime('%H:%M:%S')}] {msg}")
    if len(LOGS) > 50: LOGS.pop(0)

def manage_service(name, action):
    # Agrupar serviços em "PODs" virtuais
    pods = {
        'msa': ['msa', 'sidecar_a'],
        'sidecar_a': ['msa', 'sidecar_a'],
        'msb': ['msb', 'sidecar_b'],
        'sidecar_b': ['msb', 'sidecar_b'],
        'msc': ['msc', 'sidecar_c'],
        'sidecar_c': ['msc', 'sidecar_c']
    }
    
    targets = pods.get(name, [name])
    
    for target in targets:
        svc = SERVICES.get(target)
        if not svc: continue
        
        if action == "start":
            if not is_port_open(svc["port"]):
                # Garante limpeza total de processos fantasmas na porta antes de subir
                clean_cmd = f'for /f "tokens=5" %a in (\'netstat -ano ^| findstr :{svc["port"]} ^| findstr LISTENING\') do taskkill /f /pid %a'
                subprocess.run(clean_cmd, shell=True, capture_output=True)
                time.sleep(0.5) # Pausa para o SO liberar a porta
                
                # Constrói o comando de inicialização padrão do Django
                cmd = f'python {svc["path"]} runserver {svc["port"]}'
                SYSTEM_LOGS.append(f"TENTANDO INICIAR: {target.upper()}...")
                subprocess.Popen(cmd, shell=True, stdout=open(f"logs/{target}.log", "a"), stderr=subprocess.STDOUT)
                SYSTEM_LOGS.append(f"COMANDO ENVIADO: {target.upper()} na porta {svc['port']}")
        
        elif action == "stop":
            if is_port_open(svc["port"]):
                # No Windows, matamos pelo PID associado à porta
                cmd = f'for /f "tokens=5" %a in (\'netstat -ano ^| findstr :{svc["port"]} ^| findstr LISTENING\') do taskkill /f /pid %a'
                subprocess.run(cmd, shell=True)
                SYSTEM_LOGS.append(f"DESLIGADO: {target.upper()} na porta {svc['port']}")

    return True
    return False

def extract_traces(content):
    """Extrai blocos JSON de telemetria balanceando chaves."""
    traces = []
    stack = 0
    current_block = []
    
    for line in content.splitlines():
        if line.strip() == "{" or (line.strip().startswith("{") and "context" in line):
            stack += 1
            current_block.append(line)
        elif stack > 0:
            current_block.append(line)
            stack += line.count("{") - line.count("}")
            if stack == 0:
                block_str = "\n".join(current_block)
                if "context" in block_str:
                    traces.append(block_str)
                current_block = []
    return traces

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            with open("dashboard_ui.html", "rb") as f:
                self.wfile.write(f.read())
        elif self.path == "/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            # Verifica se os processos ainda estão ouvindo nas portas
            status = {}
            for name, svc in SERVICES.items():
                res = subprocess.run(f"netstat -ano | findstr :{svc['port']}", shell=True, capture_output=True)
                # Se não tem processo ouvindo, damos como OFF
                if "LISTENING" in res.stdout.decode():
                    status[name] = "ON"
                else:
                    status[name] = "OFF"
                    svc["proc"] = None
            self.wfile.write(json.dumps({"services": status, "logs": LOGS}).encode())
        elif self.path.startswith("/telemetry"):
            parsed = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed.query)
            sidecar = query.get("sidecar", ["c"])[0]
            log_file = f"logs/sidecar_{sidecar}.log"
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            traces = []
            if os.path.exists(log_file):
                try:
                    with open(log_file, "r") as f:
                        traces = extract_traces(f.read())
                except: pass
            
            self.wfile.write(json.dumps({"traces": traces[-10:]}).encode())
        elif self.path.startswith("/test"):
            parsed = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed.query)
            target = query.get("url", ["http://127.0.0.1:9003/proxy/alunos-escolas/"])[0]
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            start = time.time()
            try:
                # Aumentando timeout para suportar retentativas em cascata (Sidecars + Agregador)
                with httpx.Client(timeout=15.0) as client:
                    r = client.get(target, headers={"X-Request-ID": f"UI-{int(time.time())}"})
                    duration = time.time() - start
                    res = {"status": r.status_code, "duration": round(duration, 2), "data": r.json() if r.status_code == 200 else None}
            except Exception as e:
                res = {"status": "ERR", "duration": round(time.time()-start, 2), "error": str(e)}
            
            self.wfile.write(json.dumps(res).encode())

    def do_POST(self):
        if self.path == "/manage":
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length).decode())
            name = post_data.get("name")
            action = post_data.get("action")
            
            success = manage_service(name, action)
            self.send_response(200 if success else 400)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    server = HTTPServer(("0.0.0.0", 9999), DashboardHandler)
    print("DASHBOARD RODANDO EM: http://localhost:9999")
    server.serve_forever()

if __name__ == "__main__":
    if not os.path.exists("logs"): os.makedirs("logs")
    
    # Inicia todos os serviços automaticamente ao abrir o Dashboard
    print("Iniciando malha de serviços...")
    for name in SERVICES.keys():
        manage_service(name, "start")
        time.sleep(0.5) # Pequeno delay entre subidas
        
    run_server()
