from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
import httpx

class AlunosEscolasViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("agregador.services._client.get")
    def test_get_alunos_escolas_success(self, mock_get):
        # Mock SIDECAR_A (Alunos)
        mock_resp_a = MagicMock()
        mock_resp_a.status_code = 200
        mock_resp_a.json.return_value = [
            {"ra": "1001", "nome": "Ana", "codigo_turma": "T1"}
        ]
        
        # Mock SIDECAR_B (Estrutura)
        mock_resp_b = MagicMock()
        mock_resp_b.status_code = 200
        mock_resp_b.json.return_value = [
            {
                "nome": "NORTE",
                "escolas": [
                    {
                        "nome": "Escola Azul",
                        "turmas": [
                            {"codigo": "T1", "serie": "5", "turma": "A"}
                        ]
                    }
                ]
            }
        ]

        # Config sidecar calls
        mock_get.side_effect = [mock_resp_a, mock_resp_b]

        response = self.client.get("/api/alunos-escolas/")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["dre"], "NORTE")
        self.assertEqual(response.data[0]["escolas"][0]["turmas"][0]["alunos"][0]["nome"], "Ana")
        self.assertEqual(response.data[0]["escolas"][0]["turmas"][0]["serie"], "5")
        self.assertEqual(response.data[0]["escolas"][0]["turmas"][0]["turma"], "A")

    @patch("agregador.services._client.get")
    def test_get_alunos_escolas_retry_or_fail(self, mock_get):
        # Check resilience logic
        mock_resp_a = MagicMock()
        mock_resp_a.status_code = 200
        mock_resp_a.json.return_value = []
        
        # Mock sidecar B returning an error (e.g. status 503)
        mock_resp_b = MagicMock()
        mock_resp_b.status_code = 503
        mock_resp_b.raise_for_status.side_effect = httpx.HTTPError("Sidecar off")

        mock_get.side_effect = [mock_resp_a, mock_resp_b]

        response = self.client.get("/api/alunos-escolas/")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, []) # Fallback for B error is an empty list
