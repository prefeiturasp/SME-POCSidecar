from django.test import TestCase
from rest_framework.test import APIClient
from escolas.models import DRE, Escola, Turma
from escolas.serializers import DRESerializer

class EstruturaViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.dre = DRE.objects.create(nome="NORTE")
        self.escola = Escola.objects.create(nome="Escola Azul", dre=self.dre)
        self.turma1 = Turma.objects.create(codigo="T1", serie="5A", escola=self.escola)
        self.turma2 = Turma.objects.create(codigo="T2", serie="6B", escola=self.escola)

    def test_get_estrutura(self):
        response = self.client.get("/api/estrutura/")
        self.assertEqual(response.status_code, 200)
        
        dres = DRE.objects.all()
        serializer = DRESerializer(dres, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data[0]["escolas"]), 1)
        self.assertEqual(len(response.data[0]["escolas"][0]["turmas"]), 2)
        
        # Check for our new formatted fields
        turma_a = response.data[0]["escolas"][0]["turmas"][0]
        self.assertEqual(turma_a["serie"], "5")
        self.assertEqual(turma_a["turma"], "A")
