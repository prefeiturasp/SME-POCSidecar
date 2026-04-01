from django.test import TestCase
from rest_framework.test import APIClient
from alunos.models import Aluno
from alunos.serializers import AlunoSerializer

class AlunosViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.aluno1 = Aluno.objects.create(ra="1001", nome="Ana", codigo_turma="T1")
        self.aluno2 = Aluno.objects.create(ra="1002", nome="Carlos", codigo_turma="T1")

    def test_get_alunos(self):
        response = self.client.get("/api/alunos/")
        self.assertEqual(response.status_code, 200)
        
        alunos = Aluno.objects.all()
        serializer = AlunoSerializer(alunos, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(response.data), 2)
