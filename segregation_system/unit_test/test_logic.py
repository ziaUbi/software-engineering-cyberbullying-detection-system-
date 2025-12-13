import pytest
from segregation_system.prepared_session import PreparedSession
from segregation_system.learning_set_splitter import LearningSetSplitter
from segregation_system.segregation_configuration import SegregationSystemConfiguration
from segregation_system.balancing_report.balancing_report_model import BalancingReportModel
from segregation_system.coverage_report.coverage_report_model import CoverageReportModel

# Helper per creare sessioni fittizie
def make_session(label="cyberbullying", **kwargs):
    data = {
        "uuid": "0", "label": label, "tweet_length": 5,
        "word_fuck": 0, "word_bulli": 0, "word_muslim": 0, "word_gay": 0, "word_nigger": 0, "word_rape": 0,
        "event_score": 0, "event_sending-off": 0, "event_caution": 0, "event_substitution": 0, "event_foul": 0,
    }
    # Aggiungi campi audio
    for i in range(20): data[f"audio_{i}"] = 0.0
    data.update(kwargs)
    return PreparedSession(data)

def test_learning_set_splitting(monkeypatch):
    """Testa che lo splitter divida le sessioni secondo le percentuali configurate."""
    # Mock configurazione
    SegregationSystemConfiguration.LOCAL_PARAMETERS = {
        "training_set_percentage": 0.6,
        "validation_set_percentage": 0.2,
        "test_set_percentage": 0.2
    }
    
    # Crea 10 sessioni
    sessions = [make_session() for _ in range(10)]
    
    splitter = LearningSetSplitter()
    learning_set = splitter.generateLearningSets(sessions)
    
    assert len(learning_set.training_set) == 6
    assert len(learning_set.validation_set) == 2
    assert len(learning_set.test_set) == 2

def test_balancing_report_logic(monkeypatch):
    """Testa il rilevamento di classi sbilanciate."""
    SegregationSystemConfiguration.LOCAL_PARAMETERS = {
        "balancing_report_threshold": 0.1,
        "minimum_coverage_report_threshold": 2
    }
    
    # Caso Bilanciato: 3 vs 3
    sessions_balanced = [make_session("cyberbullying") for _ in range(3)] + \
                        [make_session("not_cyberbullying") for _ in range(3)]
    
    report = BalancingReportModel.generate_balancing_report(sessions_balanced)
    assert report.is_balanced is True
    assert report.is_minimum is True

    # Caso Sbilanciato: 4 vs 1
    sessions_unbalanced = [make_session("cyberbullying") for _ in range(4)] + \
                          [make_session("not_cyberbullying") for _ in range(1)]
    
    report2 = BalancingReportModel.generate_balancing_report(sessions_unbalanced)
    assert report2.is_balanced is False 
    # Dipende dalla soglia e dalla media, ma 4 vs 1 con soglia 0.1 è sbilanciato

def test_coverage_report_counters():
    """Testa che il report di copertura conti correttamente eventi e parole."""
    s1 = make_session("cyberbullying", word_fuck=2, event_foul=1)
    s2 = make_session("not_cyberbullying", word_fuck=1, event_foul=0)
    
    report = CoverageReportModel.generate_coverage_report([s1, s2])
    
    assert report.bad_words_map["fuck"] == 3  # 2 + 1
    assert report.events_map["Foul"] == 1
    assert report.total_sessions == 2