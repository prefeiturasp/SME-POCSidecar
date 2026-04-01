from django.urls import path
from .views import ProxyAlunosView

urlpatterns = [
    path("alunos/", ProxyAlunosView.as_view())
]
