import pytest
from production_system.production_phase_manager import ClassificationPhaseManager

class TestPhaseManager:
    
    def test_initialization(self):
        """Verifica l'inizializzazione corretta delle fasi."""
        pm = ClassificationPhaseManager(
            evaluation_phase=True, prod_threshold=100, eval_threshold=10
        )
        assert pm.current_phase == pm.PHASE_EVALUATION
        assert pm.evaluation_phase is True

        pm_prod = ClassificationPhaseManager(
            evaluation_phase=False, prod_threshold=100, eval_threshold=10
        )
        assert pm_prod.current_phase == pm_prod.PHASE_PRODUCTION

    def test_invalid_thresholds(self):
        """Verifica che soglie < 1 sollevino errore."""
        with pytest.raises(ValueError):
            ClassificationPhaseManager(evaluation_phase=False, prod_threshold=0, eval_threshold=10)

    def test_phase_switching_to_production(self):
        """Testa il passaggio da Evaluation a Production dopo la soglia."""
        # Configurazione: Eval Threshold = 2.
        # Significa che alla 2a sessione deve scattare lo switch.
        pm = ClassificationPhaseManager(
            evaluation_phase=True, prod_threshold=5, eval_threshold=2
        )
        
        # 1a sessione
        switched = pm.on_session_completed()
        assert not switched, "Non doveva switchare alla prima sessione"
        assert pm.eval_counter == 1, f"Eval counter dovrebbe essere 1, invece è {pm.eval_counter}"
        
        # 2a sessione (soglia raggiunta: 2 >= 2)
        switched = pm.on_session_completed()
        assert switched, f"Doveva switchare alla seconda sessione (Counter: {pm.eval_counter})"
        assert pm.current_phase == pm.PHASE_PRODUCTION
        assert pm.eval_counter == 0 # Reset avvenuto

    def test_phase_switching_to_evaluation(self):
        """Testa il passaggio da Production a Evaluation."""
        # Configurazione: Prod Threshold = 2.
        pm = ClassificationPhaseManager(
            evaluation_phase=False, prod_threshold=2, eval_threshold=5
        )
        
        # 1a sessione
        switched = pm.on_session_completed()
        assert not switched
        assert pm.prod_counter == 1
        
        # 2a sessione
        switched = pm.on_session_completed()
        assert switched, "Doveva switchare da Production a Evaluation"
        assert pm.current_phase == pm.PHASE_EVALUATION
        assert pm.prod_counter == 0