import pytest
from segregation_system.segregation_orchestrator import SegregationSystemOrchestrator
from segregation_system.segregation_configuration import SegregationSystemConfiguration

# Fake classes to mock messaging system and database handler
class FakeBroker:
    def __init__(self):
        self.sent_messages = []
        self.config_sent = []
        self._incoming_messages = []
    
    def start_server(self): pass
    
    def get_last_message(self):
        if self._incoming_messages:
            message = self._incoming_messages.pop(0)["message"]
            last_message = {
                'ip': "127.0.0.1",
                'port': 5000,
                'message': message
            }
            return last_message
        return None
    
    def send_message(self, ip, port, message, dest="send"):
        self.sent_messages.append((ip, port, message))
        return {"status": "ok"}
    
    def send_configuration(self, msg):
        self.config_sent.append(msg)

class FakeDB:
    def __init__(self):
        self.sessions = []
        self.removed = False
        
    def store_prepared_session(self, s):
        self.sessions.append(s)
        
    def get_number_of_sessions_stored(self):
        return len(self.sessions)
        
    def get_all_prepared_sessions(self):
        return self.sessions
        
    def remove_all_prepared_sessions(self):
        self.sessions = []
        self.removed = True

def test_orchestrator_flow(monkeypatch):
    """Complete test of the flow: reception -> store -> threshold check -> send learning set."""
    SegregationSystemConfiguration.LOCAL_PARAMETERS = {"min_sessions_for_processing": 1}
    SegregationSystemConfiguration.GLOBAL_PARAMETERS = {
        "Development System": {"ip": "1.2.3.4", "port": 9999},
        "Messaging System": {"ip": "1.2.3.4", "port": 8888}
    }
    
    # Mocking components
    monkeypatch.setattr("segregation_system.segregation_orchestrator.SessionReceiverAndConfigurationSender", FakeBroker)
    monkeypatch.setattr("segregation_system.segregation_orchestrator.PreparedSessionDatabaseController", FakeDB)
    
    # Avoid file I/O by mocking JSON handler methods
    state = {"service_flag": True, "enough_collected_sessions": "-", "balancing_report": "-", "coverage_report": "-"}
    monkeypatch.setattr("segregation_system.segregation_orchestrator.SegregationSystemJsonHandler.read_field_from_json", 
                        lambda path, field: state.get(field))
    monkeypatch.setattr("segregation_system.segregation_orchestrator.SegregationSystemJsonHandler.write_field_to_json", 
                        lambda path, field, val: state.update({field: val}))
    monkeypatch.setattr("segregation_system.segregation_orchestrator.SegregationSystemJsonHandler.validate_json", 
                        lambda data, schema: True) 
    
    # Avoid showing plots during tests
    monkeypatch.setattr("segregation_system.segregation_orchestrator.BalancingReportView.show_balancing_report", lambda m, w: None)
    monkeypatch.setattr("segregation_system.segregation_orchestrator.CoverageReportView.show_coverage_report", lambda m, w: None)
    
    # Force random to 0 for deterministic behavior in tests
    monkeypatch.setattr("segregation_system.segregation_orchestrator.randrange", lambda x: 0)

    orch = SegregationSystemOrchestrator(testing=True)
    
    fake_msg = {
        "message": {
            "uuid": "Test", "label": "cyberbullying", "tweet_length": 5, 
            "word_fuck": 0, "word_bulli": 0, "word_muslim": 0, "word_gay": 0, "word_nigger": 0, "word_rape": 0,
            "event_score": 0, "event_sending-off": 0, "event_caution": 0, "event_substitution": 0, "event_foul": 0,
            "audio_0": 0.0, "audio_1": 0.0, "audio_2": 0.0, "audio_3": 0.0, "audio_4": 0.0, "audio_5": 0.0, 
            "audio_6": 0.0, "audio_7": 0.0, "audio_8": 0.0, "audio_9": 0.0, "audio_10": 0.0, "audio_11": 0.0, 
            "audio_12": 0.0, "audio_13": 0.0, "audio_14": 0.0, "audio_15": 0.0, "audio_16": 0.0, "audio_17": 0.0, 
            "audio_18": 0.0, "audio_19": 0.0
        }
    }
    orch.message_broker._incoming_messages.append(fake_msg)
    orch.run()

    assert orch.db.get_number_of_sessions_stored() == 0 # It's zero because they have been processed and removed
    assert orch.db.removed is True
    
    # The state must have been reset
    assert state["enough_collected_sessions"] == "-"
