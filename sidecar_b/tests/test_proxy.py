from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
import httpx
import pybreaker

class ProxyEstruturaTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("proxy.views.get")
    def test_proxy_estrutura_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [{"nome": "NORTE"}]
        mock_get.return_value = mock_resp

        response = self.client.get("/proxy/estrutura/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["nome"], "NORTE")

    @patch("proxy.views.get")
    def test_proxy_estrutura_http_error(self, mock_get):
        mock_get.side_effect = httpx.RequestError("Host not found")

        response = self.client.get("/proxy/estrutura/")
        self.assertEqual(response.status_code, 502)

    @patch("proxy.views.breaker.call")
    def test_proxy_estrutura_circuit_breaker_open(self, mock_call):
        mock_call.side_effect = pybreaker.CircuitBreakerError()

        response = self.client.get("/proxy/estrutura/")
        self.assertEqual(response.status_code, 503)

    def test_proxy_estrutura_unexpected_error(self):
        with patch("proxy.views.breaker.call") as mock_call:
            mock_call.side_effect = Exception("General Error")
            response = self.client.get("/proxy/estrutura/")
            self.assertEqual(response.status_code, 500)
