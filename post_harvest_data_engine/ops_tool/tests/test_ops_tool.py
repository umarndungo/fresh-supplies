"""
Unit tests for FreshOps AI Operational Intelligence Engine.
Validates telemetry ingestion, cold-chain threshold breaches,
market diversion economics, AI Copilot offline reasoning, and PDF generation.
"""

import os
from pathlib import Path
import pytest
import pandas as pd
import ops_engine


@pytest.fixture
def sample_data():
    df, market_prices_df, market_dest_df = ops_engine.load_operational_data()
    return df, market_prices_df, market_dest_df


def test_data_ingestion_and_flags(sample_data):
    df, market_prices, market_dest = sample_data
    assert not df.empty, "Operational dataset should not be empty"
    assert "shipment_id" in df.columns, "shipment_id column must be present"
    assert "temp_breach" in df.columns, "temp_breach flag must be computed"
    assert "transit_delay" in df.columns, "transit_delay flag must be computed"
    assert "operational_alert" in df.columns, "operational_alert flag must be computed"

    # Verify breach logic
    high_temp_rows = df[df["Temperature_C"] > ops_engine.ALERT_TEMP_THRESHOLD]
    assert (high_temp_rows["temp_breach"] == True).all(), "All rows above threshold must be flagged as temp_breach"


def test_kpi_calculations(sample_data):
    df, _, _ = sample_data
    kpis = ops_engine.calculate_kpis(df)

    assert kpis["total_shipments"] == len(df)
    assert kpis["at_risk_count"] <= kpis["total_shipments"]
    assert kpis["temp_breaches"] >= 0
    assert kpis["total_value_kes"] > 0
    assert kpis["revenue_at_risk_kes"] >= 0
    assert kpis["estimated_salvage_kes"] <= kpis["revenue_at_risk_kes"]
    assert isinstance(kpis["avg_temperature"], float)


def test_market_diversion_ranking(sample_data):
    df, market_prices, market_dest = sample_data
    if market_dest.empty or market_prices.empty:
        pytest.skip("Market data missing for diversion test")

    row = df.iloc[0]
    recs = ops_engine.recommend_alternative_market(row, market_prices, market_dest)

    assert len(recs) > 0, "Should return at least one destination recommendation"
    # Ensure ranked by salvage revenue descending
    salvages = [r["salvage_revenue_100kg"] for r in recs]
    assert salvages == sorted(salvages, reverse=True), "Recommendations must be sorted descending by net salvage revenue"
    assert "distance_km" in recs[0]
    assert recs[0]["distance_km"] >= 0


def test_ops_copilot_offline_reasoning(sample_data):
    df, market_prices, _ = sample_data

    # Test cold-chain inquiry
    res_breach = ops_engine.query_ops_copilot("What are the cold chain breaches?", df, market_prices)
    assert "answer" in res_breach
    assert "Cold-Chain Breach" in res_breach["answer"]

    # Test crop inquiry
    res_crop = ops_engine.query_ops_copilot("Analyze tomato shipments", df, market_prices)
    assert "answer" in res_crop
    assert "Tomato" in res_crop["answer"]

    # Test revenue inquiry
    res_rev = ops_engine.query_ops_copilot("What is our revenue salvage potential?", df, market_prices)
    assert "answer" in res_rev
    assert "Revenue" in res_rev["answer"]

    # Test general briefing
    res_gen = ops_engine.query_ops_copilot("Give me an executive briefing", df, market_prices)
    assert "answer" in res_gen
    assert "Executive Briefing" in res_gen["answer"]


def test_pdf_report_generation(sample_data, tmp_path):
    df, _, _ = sample_data
    test_pdf = tmp_path / "test_report.pdf"

    generated_path = ops_engine.generate_operational_pdf_report(df, str(test_pdf))
    assert Path(generated_path).exists(), "PDF report file must be written"
    assert Path(generated_path).stat().st_size > 1000, "PDF report should not be empty"
