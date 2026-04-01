import httpx
import time

SIDECAR_A = "http://127.0.0.1:9001/proxy/alunos/"
SIDECAR_B = "http://127.0.0.1:9002/proxy/estrutura/"

_client = httpx.Client()

class AgregadorService:
    @staticmethod
    def get_dados_agregados(request_id=None):
        headers = {}
        if request_id:
            headers["X-Request-ID"] = request_id

        estado_malha = "OK"
        
        # Fetch Alunos
        try:
            r_alunos = _client.get(SIDECAR_A, headers=headers, timeout=10.0)
            r_alunos.raise_for_status()
            alunos = r_alunos.json()
        except Exception as e:
            print(f"[{request_id}] SIDECAR_A indisponível: {e}")
            alunos = []
            estado_malha = "ALUNOS INDISPONÍVEIS (Sidecar A FALHOU)"

        # Fetch Estrutura
        try:
            r_estrutura = _client.get(SIDECAR_B, headers=headers, timeout=10.0)
            r_estrutura.raise_for_status()
            estrutura = r_estrutura.json()
        except Exception as e:
            print(f"[{request_id}] SIDECAR_B indisponível: {e}")
            estado_malha = "ESTRUTURA EM MODO DE CONTINGÊNCIA (Sidecar B FALHOU)"
            # Contingência
            estrutura = [{"nome": "ESTRUTURA EM MODO DE CONTINGÊNCIA", "escolas": [{"nome": "DADOS PARCIAIS", "turmas": []}]}]
            if alunos:
                todas_turmas_ids = set([a.get("codigo_turma") for a in alunos])
                for tid in todas_turmas_ids:
                    estrutura[0]["escolas"][0]["turmas"].append({
                        "codigo": tid, "serie": "", "turma": ""
                    })

        # Alinhamento
        alunos_por_turma = {}
        for aluno in alunos:
            turma = aluno.get("codigo_turma")
            if turma not in alunos_por_turma:
                alunos_por_turma[turma] = []
            alunos_por_turma[turma].append({
                "ra": aluno.get("ra"),
                "nome": aluno.get("nome")
            })

        resultado = []
        for dre in estrutura:
            dre_obj = {
                "dre": dre.get("nome", ""),
                "escolas": []
            }
            for escola in dre.get("escolas", []):
                escola_obj = {
                    "escola": escola.get("nome", ""),
                    "turmas": []
                }
                for turma in escola.get("turmas", []):
                    codigo_turma = turma.get("codigo", "")
                    escola_obj["turmas"].append({
                        "serie": turma.get("serie", ""),
                        "turma": turma.get("turma", ""),
                        "alunos": alunos_por_turma.get(codigo_turma, [])
                    })
                dre_obj["escolas"].append(escola_obj)
            resultado.append(dre_obj)

        # Adiciona flag de status da malha para o Dashboard saber o que ocorreu
        if estado_malha != "OK":
            resultado.insert(0, {"INFO_ESTADO_MALHA": estado_malha})

        return resultado
