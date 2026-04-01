import httpx

from rest_framework.views import APIView
from rest_framework.response import Response


SIDECAR_A = "http://127.0.0.1:9001/proxy/alunos/"
SIDECAR_B = "http://127.0.0.1:9002/proxy/estrutura/"


from .services import AgregadorService

class AlunosEscolasView(APIView):
    def get(self, request):
        request_id = request.headers.get("X-Request-ID")
        print(f"[{request_id}] MSC")
        
        resultado = AgregadorService.get_dados_agregados(request_id)
        
        return Response(resultado)
