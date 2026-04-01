import logging
from contextvars import ContextVar

request_id_ctx = ContextVar("request_id", default=None)
service_ctx = ContextVar("service", default="unknown")


class ContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx.get()
        record.service = service_ctx.get()
        return True
