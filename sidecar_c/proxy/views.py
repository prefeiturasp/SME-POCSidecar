import logging
import httpx
import pybreaker

from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from rest_framework.views import APIView
from rest_framework.response import Response

from sidecar_c.http_client import get_sync


# =========================
# CONFIG
# =========================

MSC_URL = "http://127.0.0.1:8003"

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
def call_msc():
    # Agora síncrono.
    response = get_sync(f"{MSC_URL}/api/alunos-escolas/")
    response.raise_for_status()
    return response.json()


# =========================
# VIEW
# =========================

class ProxyAgregadorView(APIView):

    def get(self, request):

        logger.info("SIDECAR C - request recebido")

        try:
            # 100% síncrono.
            data = breaker.call(call_msc)

        except pybreaker.CircuitBreakerError:
            logger.error("CIRCUIT OPEN - MSC indisponível")

            return Response(
                {"erro": "MSC indisponível (circuit open)"},
                status=503
            )

        except (httpx.RequestError, RetryError) as e:
            logger.error(f"ERRO HTTP/RETRY: {str(e)}")

            return Response(
                {"erro": "Erro de comunicação com MSC"},
                status=502
            )

        except Exception as e:
            logger.error(f"ERRO INESPERADO: {str(e)}")

            return Response(
                {"erro": "Erro interno no sidecar"},
                status=500
            )

        logger.info("SIDECAR C - resposta OK")

        return Response(data)
