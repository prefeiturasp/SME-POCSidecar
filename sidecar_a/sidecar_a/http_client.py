import httpx
from .logging_context import request_id_ctx

def get_sync(url: str) -> httpx.Response:
    headers = {}
    req_id = request_id_ctx.get()
    if req_id is not None:
        headers["X-Request-ID"] = req_id

    # Usando cliente síncrono para evitar problemas de loop de eventos com OTel no Windows
    with httpx.Client() as client:
        return client.get(url, headers=headers)

def post_sync(url: str, payload: dict) -> httpx.Response:
    headers = {}
    req_id = request_id_ctx.get()
    if req_id is not None:
        headers["X-Request-ID"] = req_id

    with httpx.Client() as client:
        return client.post(url, json=payload, headers=headers)
