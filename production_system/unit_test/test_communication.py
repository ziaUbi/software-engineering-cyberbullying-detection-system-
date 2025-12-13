import pytest
from unittest.mock import patch, MagicMock
from production_system.production_system_communication import ProductionSystemIO
from production_system.label import Label

class TestCommunication:
    
    @pytest.fixture
    def io_system(self):
        return ProductionSystemIO(port=5000)

    @patch("requests.post")
    def test_send_label_to_eval(self, mock_post, io_system):
        """
        Verifica che l'invio all'Evaluation System (rule='send')
        usi un DIZIONARIO nel payload, non una stringa.
        """
        label = Label(uuid="test-uuid", label="safe")
        target_ip = "1.2.3.4"
        target_port = 8080
        
        # Mock response success
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_response

        io_system.send_label(target_ip, target_port, label, rule="send")

        # Verifica chiamata requests
        args, kwargs = mock_post.call_args
        assert args[0] == f"http://{target_ip}:{target_port}/send"
        
        payload_sent = kwargs['json']
        # QUI il controllo fondamentale: il campo 'message' deve essere un dict
        assert isinstance(payload_sent['message'], dict)
        assert payload_sent['message']['uuid'] == "test-uuid"

    @patch("requests.post")
    def test_send_label_to_client(self, mock_post, io_system):
        """
        Verifica che l'invio al Client (rule='client')
        usi una STRINGA JSON nel payload (come da specifica legacy).
        """
        label = Label(uuid="test-uuid", label="safe")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        io_system.send_label("1.2.3.4", 8080, label, rule="client")

        _, kwargs = mock_post.call_args
        payload_sent = kwargs['json']
        # QUI il controllo: per il client deve essere str
        assert isinstance(payload_sent['message'], str)
        assert "test-uuid" in payload_sent['message']

    def test_receive_message(self, io_system):
        """Testa la ricezione tramite client di test Flask."""
        client = io_system.app.test_client()
        
        response = client.post("/send", json={
            "port": 9090,
            "message": "some_content"
        })
        
        assert response.status_code == 200
        assert not io_system.msg_queue.empty()
        
        msg = io_system.msg_queue.get()
        assert msg['port'] == 9090
        assert msg['message'] == "some_content"