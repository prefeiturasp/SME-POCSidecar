import httpx
import time

SIDECAR_A = "http://127.0.0.1:9001/proxy/alunos/"
SIDECAR_B = "http://127.0.0.1:9002/proxy/estrutura/"

class AgregadorService:
    @staticmethod
    def get_dados_agregados(request_id=None):
        headers = {}
        if request_id:
            headers["X-Request-ID"] = request_id

        estado_malha = "OK"
        print(f"[{request_id}] AGREGADOR ATIVADO - PROCESSANDO MALHA...")
        alunos = []
        estrutura = []
        
        # Instanciar cliente local para evitar deadlocks no Windows com poucas threads
        with httpx.Client(timeout=10.0) as client:
            # Fetch Alunos
            try:
                r_alunos = client.get(SIDECAR_A, headers=headers)
                r_alunos.raise_for_status()
                alunos = r_alunos.json()
            except Exception as e:
                print(f"[{request_id}] SIDECAR_A indisponível: {e}")
                alunos = []
                estado_malha = "ALUNOS INDISPONÍVEIS (Sidecar A FALHOU)"

            # Fetch Estrutura
            try:
                r_estrutura = client.get(SIDECAR_B, headers=headers)
                r_estrutura.raise_for_status()
                estrutura = r_estrutura.json()
            except Exception as e:
                print(f"[{request_id}] SIDECAR_B indisponível: {e}")
                estado_malha = "ESTRUTURA EM MODO DE CONTINGÊNCIA (Sidecar B FALHOU)"
                estrutura = [{"nome": "ESTRUTURA EM MODO DE CONTINGÊNCIA", "escolas": [{"nome": "DADOS PARCIAIS", "turmas": []}]}]
                if alunos:
                    todas_turmas_ids = set([a.get("codigo_turma") for a in alunos])
                    for tid in todas_turmas_ids:
                        estrutura[0]["escolas"][0]["turmas"].append({"codigo": tid, "serie": "", "turma": ""})

        # Alinhamento (Merge)
        alunos_por_turma = {}
        for aluno in alunos:
            turma_id = aluno.get("codigo_turma")
            if turma_id not in alunos_por_turma:
                alunos_por_turma[turma_id] = []
            alunos_por_turma[turma_id].append({
                "ra": aluno.get("ra"),
                "nome": aluno.get("nome")
            })

        resultado = []
        for dre in estrutura:
            dre_obj = {
                "dre": dre.get("nome", ""),
                "escolas": []
            }
            # Bug da segunda turma? Vou garantir que percorra TODAS as escolas e TODAS as turmas
            escolas_list = dre.get("escolas", [])
            for escola in escolas_list:
                escola_obj = {
                    "escola": escola.get("nome", ""),
                    "turmas": []
                }
                turmas_list = escola.get("turmas", [])
                for turma_item in turmas_list:
                    c_turma = turma_item.get("codigo", "")
                    escola_obj["turmas"].append({
                        "serie": turma_item.get("serie", ""),
                        "turma": turma_item.get("turma", ""),
                        "alunos": alunos_por_turma.get(c_turma, [])
                    })
                dre_obj["escolas"].append(escola_obj)
            resultado.append(dre_obj)

        if estado_malha != "OK":
            resultado.insert(0, {"INFO_ESTADO_MALHA": estado_malha})

        return resultado
