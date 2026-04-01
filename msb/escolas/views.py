from rest_framework.views import APIView
from rest_framework.response import Response
from .models import DRE
from .serializers import DRESerializer
from .services import EstruturaService

class EstruturaView(APIView):
    def get(self, request):
        dres = EstruturaService.get_all_dres()
        serializer = DRESerializer(dres, many=True)
        return Response(serializer.data)
