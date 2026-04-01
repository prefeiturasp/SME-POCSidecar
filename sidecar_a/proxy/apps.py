from django.apps import AppConfig


class ProxyConfig(AppConfig):
    name = 'proxy'

    def ready(self):
        import os
        if os.environ.get('RUN_MAIN'):  # Garante que só inicialize uma vez no dev server
            try:
                from opentelemetry import trace
                from opentelemetry.sdk.trace import TracerProvider
                from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
                from opentelemetry.instrumentation.django import DjangoInstrumentor
                from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

                # Setup do provedor global de tracing
                provider = TracerProvider()
                
                # Exporter que joga os logs de trace no terminal para evidenciar a POC
                processor = SimpleSpanProcessor(ConsoleSpanExporter())
                provider.add_span_processor(processor)
                
                trace.set_tracer_provider(provider)

                # Instrumenta os pacotes automaticamente
                if not DjangoInstrumentor().is_instrumented_by_opentelemetry:
                    DjangoInstrumentor().instrument()
                if not HTTPXClientInstrumentor().is_instrumented_by_opentelemetry:
                    HTTPXClientInstrumentor().instrument()
                    
                print("[OpenTelemetry] Telemetria inicializada com Sucesso!")
            except Exception as e:
                print("[OpenTelemetry] Erro ao iniciar telemetria:", e)
