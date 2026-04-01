from django.urls import path
from .views import ProxyAgregadorView

urlpatterns = [
    path("alunos-escolas/", ProxyAgregadorView.as_view())
]
