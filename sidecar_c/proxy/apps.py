from django.apps import AppConfig


class ProxyConfig(AppConfig):
    name = 'proxy'

    def ready(self):
        import os
        if os.environ.get('RUN_MAIN'):
            try:
                from opentelemetry import trace
                from opentelemetry.sdk.trace import TracerProvider
                from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
                from opentelemetry.instrumentation.django import DjangoInstrumentor
                from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

                provider = TracerProvider()
                processor = SimpleSpanProcessor(ConsoleSpanExporter())
                provider.add_span_processor(processor)
                trace.set_tracer_provider(provider)

                if not DjangoInstrumentor().is_instrumented_by_opentelemetry:
                    DjangoInstrumentor().instrument()
                if not HTTPXClientInstrumentor().is_instrumented_by_opentelemetry:
                    HTTPXClientInstrumentor().instrument()
                print("[OpenTelemetry] Telemetria inicializada no SIDECAR C com Sucesso!")
            except Exception as e:
                print("[OpenTelemetry] Erro ao iniciar telemetria:", e)
