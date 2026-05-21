import pandas as pd

from backend.app.services.evidence import build_evidence_package


def sample_clean_stats() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "rank": 1,
            "lane": "Mid",
            "hero": "Cecilion",
            "tier": "S",
            "win_rate": 55.0,
            "ban_rate": 20.0,
            "pick_rate": 8.0,
            "roles": "Mage",
        },
        {
            "rank": 2,
            "lane": "Gold",
            "hero": "Granger",
            "tier": "A",
            "win_rate": 51.0,
            "ban_rate": 40.0,
            "pick_rate": 15.0,
            "roles": "Marksman",
        },
        {
            "rank": 3,
            "lane": "Mid",
            "hero": "Lylia",
            "tier": "A",
            "win_rate": 55.0,
            "ban_rate": 5.0,
            "pick_rate": 3.0,
            "roles": "Mage",
        },
        {
            "rank": 4,
            "lane": "Roam",
            "hero": "Tigreal",
            "tier": "B",
            "win_rate": 48.0,
            "ban_rate": 10.0,
            "pick_rate": 20.0,
            "roles": "Tank",
        },
    ])


def test_evidence_package_contains_expected_top_level_sections():
    df = sample_clean_stats()

    evidence = build_evidence_package(df, issue_count=2)

    assert evidence["row_count"] == 4
    assert evidence["issue_count"] == 2

    assert "summary_stats" in evidence
    assert "lane_distribution" in evidence
    assert "top_win_rate" in evidence
    assert "top_ban_rate" in evidence
    assert "top_pick_rate" in evidence
    assert "high_win_low_pick" in evidence


def test_evidence_package_summarizes_rates_and_lane_distribution():
    df = sample_clean_stats()

    evidence = build_evidence_package(df, issue_count=0)

    assert evidence["summary_stats"]["win_rate_mean"] == 52.25
    assert evidence["summary_stats"]["ban_rate_mean"] == 18.75
    assert evidence["summary_stats"]["pick_rate_mean"] == 11.5

    assert evidence["summary_stats"]["win_rate_median"] == 53.0
    assert evidence["summary_stats"]["ban_rate_median"] == 15.0
    assert evidence["summary_stats"]["pick_rate_median"] == 11.5

    assert evidence["lane_distribution"] == {
        "Mid": 2,
        "Gold": 1,
        "Roam": 1,
    }


def test_evidence_package_ranks_heroes_by_relevant_metrics():
    df = sample_clean_stats()

    evidence = build_evidence_package(df, issue_count=0)

    assert evidence["top_win_rate"][0]["hero"] in {"Cecilion", "Lylia"}
    assert evidence["top_win_rate"][0]["win_rate"] == 55.0

    assert evidence["top_ban_rate"][0]["hero"] == "Granger"
    assert evidence["top_ban_rate"][0]["ban_rate"] == 40.0

    assert evidence["top_pick_rate"][0]["hero"] == "Tigreal"
    assert evidence["top_pick_rate"][0]["pick_rate"] == 20.0


def test_evidence_package_high_win_low_pick_prioritizes_lower_pick_when_win_rate_ties():
    df = sample_clean_stats()

    evidence = build_evidence_package(df, issue_count=0)

    first = evidence["high_win_low_pick"][0]

    assert first["hero"] == "Lylia"
    assert first["win_rate"] == 55.0
    assert first["pick_rate"] == 3.0


def test_evidence_package_handles_empty_dataframe():
    df = pd.DataFrame(columns=[
        "rank",
        "lane",
        "hero",
        "tier",
        "win_rate",
        "ban_rate",
        "pick_rate",
        "roles",
    ])

    evidence = build_evidence_package(df, issue_count=3)

    assert evidence["row_count"] == 0
    assert evidence["issue_count"] == 3

    assert evidence["summary_stats"]["win_rate_mean"] is None
    assert evidence["summary_stats"]["ban_rate_mean"] is None
    assert evidence["summary_stats"]["pick_rate_mean"] is None

    assert evidence["lane_distribution"] == {}
    assert evidence["top_win_rate"] == []
    assert evidence["top_ban_rate"] == []
    assert evidence["top_pick_rate"] == []
    assert evidence["high_win_low_pick"] == []