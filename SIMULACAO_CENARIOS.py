import time
import httpx
import sys

BASE_URL = "http://127.0.0.1:9003/proxy/alunos-escolas/"
SIDECAR_A = "http://127.0.0.1:9001/proxy/alunos/"

def print_header(text):
    print("\n" + "="*80)
    print(f" {text.upper()} ")
    print("="*80)

def run_request(url, label):
    print(f"\n[REQ] Chamando {label} ({url})...")
    start = time.time()
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, headers={"X-Request-ID": f"DEMO-{int(time.time())}"})
            duration = time.time() - start
            print(f"[RES] Status: {resp.status_code} | Tempo: {duration:.2f}s")
            if resp.status_code == 200:
                print("[RES] Dados recebidos com sucesso!")
                # print(resp.json()) # Opcional: mostrar JSON
            elif resp.status_code == 502:
                print("[RES] ERRO: Bad Gateway (O Sidecar tentou retentativas e falhou)")
            elif resp.status_code == 503:
                print("[RES] ERRO: Service Unavailable (Circuit Breaker Aberto ou Serviço fora)")
            else:
                print(f"[RES] Erro Inesperado: {resp.status_code}")
    except Exception as e:
        print(f"[ERROR] Falha de conexão: {e}")

def main():
    print_header("Apresentação de Cenários da POC Sidecar")
    print("Certifique-se de que 'python run_all.py' está rodando!")
    
    input("\n[Pressione ENTER para Cenário 1: Sucesso Total]")
    run_request(BASE_URL, "Agregador (Sidecar C)")

    print("\n[INSTRUÇÃO] Agora, simule uma falha: Finalize o processo do 'msa' (Porta 8001).")
    input("[Pressione ENTER quando o MSA estiver desligado]")
    
    print_header("Cenário 2: Resiliência e Retries")
    print("O Sidecar A tentará reconectar ao MSA por 3 vezes antes de desistir.")
    run_request(BASE_URL, "Agregador (Sidecar C)")

    print("\n[INSTRUÇÃO] Note que o pedido acima demorou ~3 segundos (Retries).")
    print("Vamos forçar a abertura do Circuit Breaker chamando o Sidecar A repetidamente.")
    input("[Pressione ENTER para forçar Circuit Breaker]")
    
    for i in range(5):
        print(f"Tentativa {i+1}...")
        run_request(SIDECAR_A, "Sidecar A (Alunos)")
        time.sleep(0.5)

    print_header("Cenário 3: Circuit Breaker Aberto (Fail-Fast)")
    print("Agora as chamadas devem ser INSTANTÂNEAS com erro 503, sem tentar o MSA.")
    run_request(BASE_URL, "Agregador (Sidecar C)")

    print("\n[INSTRUÇÃO] Agora, suba o MSA novamente (ou rode 'run_all.py' de novo).")
    input("[Pressione ENTER quando o MSA estiver de volta]")
    
    print_header("Cenário 4: Recuperação do Circuito")
    print("Aguardando o período de cooldown do Circuit Breaker...")
    time.sleep(5)
    run_request(BASE_URL, "Agregador (Sidecar C)")

    print("\nAPRESENTAÇÃO CONCLUÍDA!")

if __name__ == "__main__":
    main()
