import logging
import httpx
import pybreaker

from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from rest_framework.views import APIView
from rest_framework.response import Response

from sidecar_a.http_client import get_sync


# =========================
# CONFIG
# =========================

MSA_URL = "http://127.0.0.1:8001"

logger = logging.getLogger(__name__)

breaker = pybreaker.CircuitBreaker(
    fail_max=3,
    reset_timeout=10
)


# =========================
# HTTP CALL
# =========================

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5)
)
def call_msa():
    # Agora síncrono. Tenacity lida perfeitamente com Exceptions.
    response = get_sync(f"{MSA_URL}/api/alunos/")
    response.raise_for_status()
    return response.json()


# =========================
# VIEW
# =========================

class ProxyAlunosView(APIView):

    def get(self, request):

        logger.info("SIDECAR A - request recebido")

        try:
            # Chamada síncrona dentro do orquestrador pybreaker
            data = breaker.call(call_msa)
            
        except pybreaker.CircuitBreakerError:
            logger.error("CIRCUIT OPEN - MSA indisponível")

            return Response(
                {"erro": "MSA indisponível (circuit open)"},
                status=503
            )

        except (httpx.RequestError, RetryError) as e:
            logger.error(f"ERRO HTTP/RETRY: {str(e)}")

            return Response(
                {"erro": "Erro de comunicação com MSA"},
                status=502
            )

        except Exception as e:
            logger.error(f"ERRO INESPERADO: {str(e)}")

            return Response(
                {"erro": "Erro interno no sidecar"},
                status=500
            )

        logger.info("SIDECAR A - resposta OK")

        return Response(data)