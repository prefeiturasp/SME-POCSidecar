from django.urls import path
from .views import AlunosView

urlpatterns = [
    path('alunos/', AlunosView.as_view()),
]
