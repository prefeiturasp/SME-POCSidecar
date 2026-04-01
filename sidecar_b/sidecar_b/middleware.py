import uuid
from .logging_context import request_id_ctx, service_ctx


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.request_id = request_id

        response = self.get_response(request)
        response["X-Request-ID"] = request_id

        return response


class LoggingContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id_ctx.set(request.request_id)

        service_ctx.set("sidecar-b")

        return self.get_response(request)
