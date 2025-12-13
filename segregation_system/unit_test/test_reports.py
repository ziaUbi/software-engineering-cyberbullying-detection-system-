from pathlib import Path

import pytest

from segregation_system.balancing_report.balancing_report_model import BalancingReportModel
from segregation_system.coverage_report.coverage_report_model import CoverageReportModel
from segregation_system.balancing_report.balancing_report_view import BalancingReportView
from segregation_system.coverage_report.coverage_report_view import CoverageReportView
from segregation_system.coverage_report.coverage_report import CoverageReportData
from segregation_system.balancing_report.balancing_report import BalancingReportData
from segregation_system.segregation_configuration import SegregationSystemConfiguration


def _make_session(label: str, tweet_length: int = 10, **overrides) -> dict:
    base = {
        "uuid": "00000000-0000-0000-0000-000000000000",
        "label": label,
        "tweet_length": tweet_length,
        "word_fuck": 0,
        "word_bulli": 0,
        "word_muslim": 0,
        "word_gay": 0,
        "word_nigger": 0,
        "word_rape": 0,
        "event_score": 0,
        "event_sending_off": 0,
        "event_caution": 0,
        "event_substitution": 0,
        "event_foul": 0,
    }
    base.update({f"audio_{i}": 0.0 for i in range(20)})
    base.update(overrides)
    return base


def test_balancing_report_flags(monkeypatch: pytest.MonkeyPatch):
    SegregationSystemConfiguration.LOCAL_PARAMETERS = {
        "balancing_report_threshold": 0.10,
        "minimum_coverage_report_threshold": 2,
    }

    # 6 sessions: 3 vs 3 is balanced and minimum ok
    sessions = [_make_session("cyberbullying") for _ in range(3)] + [_make_session("not_cyberbullying") for _ in range(3)]
    report = BalancingReportModel.generate_balancing_report(sessions)
    assert report.is_balanced is True
    assert report.is_minimum is True

    # 5 sessions: 4 vs 1 is not balanced and minimum not ok (class count < 2)
    sessions = [_make_session("cyberbullying") for _ in range(4)] + [_make_session("not_cyberbullying")]
    report = BalancingReportModel.generate_balancing_report(sessions)
    assert report.is_balanced is False
    assert report.is_minimum is False


def test_coverage_report_counters():
    s1 = _make_session(
        "cyberbullying",
        tweet_length=12,
        word_fuck=1,
        word_bulli=2,
        event_score=1,
        event_sending_off=1,
        audio_0=-2.4,
        audio_1=-2.6,
    )
    s2 = _make_session(
        "not_cyberbullying",
        tweet_length=12,
        word_fuck=0,
        word_bulli=1,
        event_score=2,
        event_sending_off=0,
        audio_0=-2.4,
        audio_1=None,
    )
    report = CoverageReportModel.generate_coverage_report([s1, s2])

    assert report.total_sessions == 2
    assert report.tweet_length_map[12] == 2
    assert report.bad_words_map["fuck"] == 1
    assert report.bad_words_map["bulli"] == 3
    assert report.events_map["Score"] == 3
    assert report.events_map["Sending-off"] == 1

    # audio_0 appears twice, audio_1 only once (because None is skipped)
    assert report.audio_db_map[-2] == 2  # round(-2.4)->-2 (2x)
    assert report.audio_db_map[-3] == 1  # round(-2.6)->-3 (1x)


def test_views_call_savefig(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    # Create the folder structure expected by the views (they hardcode segregation_system/<workspace_dir>/...)
    (tmp_path / "segregation_system" / "plots").mkdir(parents=True)

    saved = {}

    def fake_savefig(path, *args, **kwargs):
        saved["path"] = path

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("matplotlib.pyplot.savefig", fake_savefig)

    # Balancing report
    bal = BalancingReportData(
        total_sessions=2,
        class_distribution={"a": 1, "b": 1},
        class_percentages={"a": 50.0, "b": 50.0},
        is_minimum=True,
        is_balanced=True,
    )
    BalancingReportView.show_balancing_report(bal, "plots")
    assert saved["path"].endswith("segregation_system/plots/balancing_report.png")

    # Coverage report
    saved.clear()
    cov = CoverageReportData(
        total_sessions=1,
        tweet_length_map={10: 3},
        audio_db_map={-2: 4},
        bad_words_map={"fuck": 1},
        events_map={"Score": 1, "Sending-off": 0, "Caution": 0, "Substitution": 0, "Foul": 0},
    )
    CoverageReportView.show_coverage_report(cov, "plots")
    assert saved["path"].endswith("segregation_system/plots/coverage_report.png")