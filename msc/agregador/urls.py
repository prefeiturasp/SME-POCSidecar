from django.urls import path
from .views import AlunosEscolasView

urlpatterns = [
    path("alunos-escolas/", AlunosEscolasView.as_view())
]
