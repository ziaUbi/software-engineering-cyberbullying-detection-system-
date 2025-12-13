import json

import pytest


def test_orchestrator_happy_path_generates_and_sends_learning_sets(monkeypatch: pytest.MonkeyPatch):
    """End-to-end-ish unit test of run() using fakes.

    We avoid sockets/flask/sqlite/filesystem by mocking collaborators.
    """

    from segregation_system.segregation_orchestrator import SegregationSystemOrchestrator
    from segregation_system.balancing_report.balancing_report import BalancingReportData
    from segregation_system.coverage_report.coverage_report import CoverageReportData
    from segregation_system.learning_set import LearningSet
    from segregation_system.segregation_configuration import SegregationSystemConfiguration

    # --- Fake message broker ---
    class FakeBroker:
        def __init__(self):
            self.sent = []
            self.config_sent = []
            self._messages = []

        def start_server(self):
            return None

        def get_last_message(self):
            return self._messages.pop(0)

        def send_message(self, ip, port, message, dest="send"):
            self.sent.append((ip, port, message, dest))
            return {"status": "ok"}

        def send_configuration(self, msg: str):
            self.config_sent.append(msg)

    # --- Fake DB ---
    class FakeDB:
        def __init__(self):
            self._stored = []
            self.removed = False

        def store_prepared_session(self, s):
            self._stored.append(s)

        def get_number_of_sessions_stored(self):
            return len(self._stored)

        def get_all_prepared_sessions(self):
            # orchestrator passes these dicts to report models
            return [x for x in self._stored]

        def remove_all_prepared_sessions(self):
            self.removed = True
            self._stored.clear()

    # Patch the collaborators used in __init__
    monkeypatch.setattr(
        "segregation_system.segregation_orchestrator.SessionReceiverAndConfigurationSender",
        lambda: FakeBroker(),
    )
    monkeypatch.setattr(
        "segregation_system.segregation_orchestrator.PreparedSessionDatabaseController",
        lambda: FakeDB(),
    )

    # Avoid filesystem execution_state reads/writes
    state = {"service_flag": True, "enough_collected_sessions": "-", "balancing_report": "-", "coverage_report": "-"}

    def fake_read_field(_path, field):
        return state[field]

    def fake_write_field(_path, field, value):
        state[field] = value
        return True

    monkeypatch.setattr(
        "segregation_system.segregation_orchestrator.SegregationSystemJsonHandler.read_field_from_json",
        fake_read_field,
    )
    monkeypatch.setattr(
        "segregation_system.segregation_orchestrator.SegregationSystemJsonHandler.write_field_to_json",
        fake_write_field,
    )
    monkeypatch.setattr(
        "segregation_system.segregation_orchestrator.SegregationSystemJsonHandler.validate_json",
        lambda msg, schema: True,
    )

    # Make PreparedSession just forward dicts (avoid PreparedSession constructor issues)
    monkeypatch.setattr(
        "segregation_system.segregation_orchestrator.PreparedSession",
        lambda d: d,
    )

    # Configure minimum sessions = 1 and development system address
    SegregationSystemConfiguration.LOCAL_PARAMETERS = {"min_sessions_for_processing": 1}
    SegregationSystemConfiguration.GLOBAL_PARAMETERS = {"Development System": {"ip": "1.2.3.4", "port": 9999}}

    # Prevent run() from overwriting the injected configuration from files.
    monkeypatch.setattr(
        "segregation_system.segregation_orchestrator.SegregationSystemConfiguration.load_parameters",
        lambda: None,
    )

    # Force balanced + minimum
    monkeypatch.setattr(
        "segregation_system.segregation_orchestrator.BalancingReportModel.generate_balancing_report",
        lambda sessions: BalancingReportData(
            total_sessions=len(sessions),
            class_distribution={"a": 1},
            class_percentages={"a": 100.0},
            is_minimum=True,
            is_balanced=True,
        ),
    )
    monkeypatch.setattr(
        "segregation_system.segregation_orchestrator.CoverageReportModel.generate_coverage_report",
        lambda sessions: CoverageReportData(
            total_sessions=len(sessions),
            tweet_length_map={10: 1},
            audio_db_map={0: 1},
            bad_words_map={"fuck": 0},
            events_map={"Score": 0, "Sending-off": 0, "Caution": 0, "Substitution": 0, "Foul": 0},
        ),
    )
    # No plotting during tests
    monkeypatch.setattr("segregation_system.segregation_orchestrator.BalancingReportView.show_balancing_report", lambda *a, **k: None)
    monkeypatch.setattr("segregation_system.segregation_orchestrator.CoverageReportView.show_coverage_report", lambda *a, **k: None)

    # Coverage status in testing is randomized via randrange(1) which always returns 0 anyway,
    # but patch it to be explicit.
    monkeypatch.setattr("segregation_system.segregation_orchestrator.randrange", lambda _: 0)

    # Splitter returns a known LearningSet
    monkeypatch.setattr(
        "segregation_system.segregation_orchestrator.LearningSetSplitter",
        lambda: type(
            "FakeSplitter",
            (),
            {
                "generateLearningSets": lambda self, sessions: LearningSet(training_set=[], validation_set=[], test_set=[])
            },
        )(),
    )

    orch = SegregationSystemOrchestrator(testing=True)
    # Inject a single prepared session message into the fake broker
    orch.message_broker._messages.append({"ip": "127.0.0.1", "port": 1234, "message": {"uuid": "x"}})

    orch.run()

    # After successful run: it should have sent a message to the Development System
    assert orch.message_broker.sent, "Expected a message to be sent to Development System"
    ip, port, message, dest = orch.message_broker.sent[0]
    assert (ip, port) == ("1.2.3.4", 9999)
    # The message should be JSON
    json.loads(message)
    assert orch.db.removed is True

    # Execution state reset
    assert state["enough_collected_sessions"] == "-"
    assert state["balancing_report"] == "-"
    assert state["coverage_report"] == "-"
