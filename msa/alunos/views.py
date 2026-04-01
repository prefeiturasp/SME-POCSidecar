from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import AlunoSerializer
from .services import AlunoService

class AlunosView(APIView):
    def get(self, request):
        # SOLID: Delegation to a service provider instead of directly doing DB queries
        alunos = AlunoService.get_all_alunos()
        serializer = AlunoSerializer(alunos, many=True)
        return Response(serializer.data)
