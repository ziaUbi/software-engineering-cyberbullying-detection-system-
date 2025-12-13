import json

import pytest

from segregation_system.session_receiver_and_configuration_sender import SessionReceiverAndConfigurationSender


def test_receive_route_stores_payload_into_queue():
    broker = SessionReceiverAndConfigurationSender(host="127.0.0.1", port=5555)
    client = broker.app.test_client()

    # Route expects 'payload' key
    resp = client.post("/send", json={"port": 1234, "payload": {"hello": "world"}})
    assert resp.status_code == 200

    last = broker.get_last_message()
    assert last["port"] == 1234
    assert last["message"] == {"hello": "world"}


def test_send_message_uses_message_field(monkeypatch: pytest.MonkeyPatch):
    """Documents the current (likely buggy) behavior: payload contains 'message', not 'payload'."""

    captured = {}

    class FakeResp:
        status_code = 200

        def json(self):
            return {"status": "ok"}

    def fake_post(url, json=None, **kwargs):
        captured["url"] = url
        captured["json"] = json
        return FakeResp()

    monkeypatch.setattr("segregation_system.session_receiver_and_configuration_sender.requests.post", fake_post)

    broker = SessionReceiverAndConfigurationSender(host="127.0.0.1", port=5555)
    out = broker.send_message("10.0.0.1", 9999, "hi", dest="send")
    assert out == {"status": "ok"}

    assert captured["url"] == "http://10.0.0.1:9999/send"
    assert captured["json"]["message"] == "hi"
    assert "payload" not in captured["json"]
