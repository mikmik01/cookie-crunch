import pandas as pd

from app.services.ranker import rank_candidates


def sample_stats():
    return pd.DataFrame([
        {"hero": "A", "rank": 1, "win_rate": 54.0, "pick_rate": 20.0, "ban_rate": 5.0},
        {"hero": "B", "rank": 2, "win_rate": 54.0, "pick_rate": 4.0, "ban_rate": 3.0},
        {"hero": "C", "rank": 3, "win_rate": 50.0, "pick_rate": 6.0, "ban_rate": 45.0},
        {"hero": "D", "rank": 4, "win_rate": 48.0, "pick_rate": 3.0, "ban_rate": 42.0},
    ])


def test_underrated_ranking_prioritizes_high_win_and_low_pick():
    ranked = rank_candidates(sample_stats(), "find_underrated_heroes", top_n=2)

    assert ranked["hero"].tolist() == ["B", "A"]


def test_overbanned_ranking_prioritizes_high_ban_and_weaker_win_rate():
    ranked = rank_candidates(sample_stats(), "find_overbanned_heroes", top_n=2)

    assert ranked["hero"].tolist() == ["C", "D"]


def test_summary_ranking_uses_existing_rank_order():
    ranked = rank_candidates(sample_stats(), "summarize_meta", top_n=2)

    assert ranked["hero"].tolist() == ["A", "B"]