import pytest
from unittest.mock import MagicMock, patch
from production_system.production_orchestrator import ProductionOrchestrator
from production_system.label import Label

class TestOrchestrator:

    @pytest.fixture
    def mock_deps(self, mocker):
        """Mocka tutte le dipendenze esterne dell'orchestrator."""
        mocker.patch("production_system.production_orchestrator.ConfigurationParameters")
        mocker.patch("production_system.production_orchestrator.ProductionSystemIO")
        mocker.patch("production_system.production_orchestrator.JsonHandler")
        # Mock deployment e classification
        mocker.patch("production_system.production_orchestrator.Deployment")
        mocker.patch("production_system.production_orchestrator.Classification")
        
        return mocker

    def test_handle_deployment(self, mock_deps):
        """Testa il flusso di ricezione di un nuovo classificatore."""
        orch = ProductionOrchestrator(service=False, unit_test=True)
        
        # Simuliamo deploy successo patchando la classe Deployment importata nell'orchestrator
        with patch("production_system.production_orchestrator.Deployment") as MockDep:
            # Configuriamo il mock per restituire True al metodo deploy
            MockDep.return_value.deploy.return_value = True
            
            orch._handle_deployment("fake_payload_string")
            
            # Verifiche
            assert orch._deployed is True
            # Verifica che sia stata inviata la configurazione (notifica di aggiornamento)
            orch._prod_sys_io.send_configuration.assert_called_once()

    def test_handle_classification_flow(self, mock_deps):
        """
        Testa il flusso completo:
        Ricezione sessione -> Validazione -> Classificazione -> Invio Label -> Aggiornamento Fase
        """
        orch = ProductionOrchestrator(service=False, unit_test=True)
        orch._deployed = True # Simuliamo classificatore presente
        orch._phase_manager = MagicMock()
        orch._phase_manager.evaluation_phase = True # Siamo in fase eval
        
        # Setup validazione JSON OK
        orch._handler.validate_json.return_value = True
        
        # Setup Classificazione che ritorna una Label
        # Patchiamo la classe usata dall'orchestrator
        with patch("production_system.production_orchestrator.Classification") as MockClf:
            fake_label = Label(uuid="u1", label="safe")
            MockClf.return_value.classify.return_value = fake_label

            # Esecuzione
            fake_session = {"uuid": "u1", "tweet_length": 10}
            orch._handle_classification(fake_session)

            # Asserzioni
            # 1. Deve aver chiamato classify
            MockClf.return_value.classify.assert_called()
            
            # 2. Deve aver inviato al Client (rule='client') e all'Eval (rule='send')
            calls = orch._prod_sys_io.send_label.call_args_list
            assert len(calls) == 2
            
            rules_called = [c[0][3] for c in calls] # estrae l'argomento 'rule'
            assert "client" in rules_called
            assert "send" in rules_called

            # 3. Deve aver aggiornato il phase manager
            orch._phase_manager.on_session_completed.assert_called_once()

    def test_handle_classification_invalid_json(self, mock_deps):
        """Testa il rifiuto di sessioni non valide."""
        orch = ProductionOrchestrator(service=False, unit_test=True)
        
        # Caso 1: JSON non valido (passato come stringa malformata)
        orch._handle_classification("{invalid_json")
        orch._prod_sys_io.send_label.assert_not_called()

        # Caso 2: Schema non valido
        orch._handler.validate_json.return_value = False
        orch._handle_classification({"valid": "json", "but": "wrong_schema"})
        orch._prod_sys_io.send_label.assert_not_called()