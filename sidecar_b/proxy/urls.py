from django.urls import path
from .views import ProxyEstruturaView

urlpatterns = [
    path("estrutura/", ProxyEstruturaView.as_view())
]
