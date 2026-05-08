from report import build_report

def test_report_uses_default_headline_when_output_is_empty():
    report = build_report({})

    assert report.startswith("# MLBB Meta Report")
    assert "## Key Findings" not in report
    assert "## Summary" not in report

def test_report_renders_analyst_output_as_markdown():
    analyst_output = {
        "headline": "Mid Lane Meta Watch",
        "key_findings": [
            {
                "claim": "Cecilion is a strong ranked pick.",
                "evidence": "53.2% win rate with 8.1% pick rate.",
                "confidence": "high",
            }
        ],
        "meta_summary": "Mid-associated scaling mages are performing well.",
    }

    report = build_report(analyst_output)

    assert report.startswith("# Mid Lane Meta Watch")
    assert "## Key Findings" in report
    assert "Cecilion is a strong ranked pick." in report
    assert "53.2% win rate with 8.1% pick rate." in report
    assert "Confidence: high" in report
    assert "## Summary" in report