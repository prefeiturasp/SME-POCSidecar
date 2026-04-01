from django.urls import path
from .views import EstruturaView

urlpatterns = [
    path("estrutura/", EstruturaView.as_view())
]
