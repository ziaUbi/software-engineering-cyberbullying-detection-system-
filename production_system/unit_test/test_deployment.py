from unittest.mock import mock_open, patch
from production_system.deployment import Deployment

def test_deploy_success():
    deployment = Deployment()
    
    # Simuliamo un payload che è una stringa latin1 valida
    # '\xe0' è 'à' in latin1
    payload = "dummy_model_string_\xe0" 
    
    with patch("pathlib.Path.open", mock_open()) as mocked_file:
        result = deployment.deploy(payload)
        
        assert result is True
        # Verifica che sia stato scritto in binario ('wb')
        mocked_file.assert_called_with("wb")
        # Verifica che il contenuto sia stato codificato correttamente in bytes
        handle = mocked_file()
        handle.write.assert_called_once_with(payload.encode("latin1"))

def test_deploy_failure_oserror():
    """Testa la gestione errori I/O."""
    deployment = Deployment()
    with patch("pathlib.Path.open", side_effect=OSError("Disk full")):
        result = deployment.deploy("data")
        assert result is False