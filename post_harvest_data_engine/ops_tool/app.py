"""
FreshOps AI - Operational Intelligence & Cold-Chain Hub
Executive Glassmorphic Edition: Fresh Green Leafy Agricultural Theme
Light Mode by default for maximum executive readability and contrast.
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import ops_engine

# Page configuration
st.set_page_config(
    page_title="FreshOps AI — Executive Cold-Chain Hub",
    page_icon="🥬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Executive Glassmorphic CSS (Fresh Leafy Green Theme & High Contrast)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Import Inter font for executive typography */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Ambient Botanical Background */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(209, 250, 229, 0.7) 0%, transparent 35%),
                    radial-gradient(circle at 90% 10%, rgba(187, 247, 208, 0.6) 0%, transparent 30%),
                    radial-gradient(circle at 50% 80%, rgba(220, 252, 231, 0.7) 0%, transparent 45%),
                    linear-gradient(180deg, #f4faf4 0%, #ebf5ec 100%);
        background-attachment: fixed;
        color: #132a13;
    }

    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(243, 249, 244, 0.82) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(45, 106, 79, 0.15) !important;
        box-shadow: 4px 0 24px rgba(45, 106, 79, 0.03) !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(45, 106, 79, 0.12);
    }

    /* Header Glass Card */
    .hero-glass-card {
        background: rgba(255, 255, 255, 0.82);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 28px 32px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -5px rgba(27, 67, 50, 0.07), 0 0 0 1px rgba(45, 106, 79, 0.06);
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(135deg, rgba(45, 106, 79, 0.12) 0%, rgba(82, 183, 136, 0.18) 100%);
        color: #1b4332;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.82rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        border: 1px solid rgba(45, 106, 79, 0.2);
        margin-bottom: 12px;
    }

    .hero-title {
        font-size: 2.25rem;
        font-weight: 800;
        color: #081c15;
        letter-spacing: -0.02em;
        line-height: 1.2;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #2d6a4f;
        font-weight: 500;
        line-height: 1.5;
        max-width: 900px;
    }

    /* Glass KPI Metric Grid */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 16px;
        margin-bottom: 28px;
    }

    @media (max-width: 1200px) {
        .kpi-container { grid-template-columns: repeat(3, 1fr); }
    }
    @media (max-width: 768px) {
        .kpi-container { grid-template-columns: repeat(2, 1fr); }
    }

    .kpi-glass-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 6px 20px -2px rgba(27, 67, 50, 0.05), 0 0 0 1px rgba(45, 106, 79, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .kpi-glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 28px -4px rgba(27, 67, 50, 0.1), 0 0 0 1px rgba(45, 106, 79, 0.15);
    }

    .kpi-label {
        font-size: 0.78rem;
        font-weight: 700;
        color: #40916c;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 1.65rem;
        font-weight: 800;
        color: #081c15;
        line-height: 1.1;
        margin-bottom: 6px;
    }

    .kpi-sub {
        font-size: 0.8rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    .sub-green { color: #2d6a4f; }
    .sub-red { color: #d90429; }
    .sub-orange { color: #d97706; }

    /* Content Glass Panels */
    .glass-panel {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.9);
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 8px 24px -4px rgba(27, 67, 50, 0.05);
        margin-bottom: 24px;
    }

    /* Streamlit Tabs Customization */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(12px);
        border-radius: 14px;
        padding: 6px;
        border: 1px solid rgba(45, 106, 79, 0.12);
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 22px;
        font-weight: 700;
        color: #2d6a4f;
        border: none !important;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background: #1b4332 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(27, 67, 50, 0.25);
    }

    /* Button Styling */
    .stButton>button {
        background: linear-gradient(135deg, #2d6a4f 0%, #1b4332 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(27, 67, 50, 0.2) !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(27, 67, 50, 0.3) !important;
    }

    /* DataFrame Styling */
    [data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(45, 106, 79, 0.15);
        background: rgba(255, 255, 255, 0.9);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def get_data():
    return ops_engine.load_operational_data()


raw_df, market_prices_df, market_dest_df = get_data()

# ---------------------------------------------------------
# Sidebar: Controls, Filters & System Health
# ---------------------------------------------------------
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
    <span style="font-size: 2.2rem;">🥬</span>
    <div>
        <h3 style="margin: 0; color: #081c15; font-weight: 800; font-size: 1.3rem;">FreshOps AI</h3>
        <p style="margin: 0; color: #40916c; font-size: 0.8rem; font-weight: 600;">Horticultural Cold-Chain Suite</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Status Badge
gemini_configured = bool(os.getenv("GEMINI_API_KEY", "").strip())
if gemini_configured:
    st.sidebar.markdown("""
    <div style="background: rgba(45, 106, 79, 0.1); border: 1px solid rgba(45, 106, 79, 0.25); border-radius: 8px; padding: 8px 12px; margin-bottom: 16px;">
        <span style="color: #1b4332; font-weight: 700; font-size: 0.82rem;">⚡ AI Engine: Online (Gemini 1.5)</span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div style="background: rgba(45, 106, 79, 0.08); border: 1px solid rgba(45, 106, 79, 0.2); border-radius: 8px; padding: 8px 12px; margin-bottom: 16px;">
        <span style="color: #2d6a4f; font-weight: 700; font-size: 0.82rem;">🍃 AI Engine: Deterministic NLP (Offline)</span>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("<h4 style='color: #1b4332; margin-bottom: 8px;'>🔍 Dispatch Corridor Filter</h4>", unsafe_allow_html=True)

# Crop selector
all_crops = ["All Produce"] + sorted(list(raw_df["crop_type"].dropna().unique()))
selected_crop = st.sidebar.selectbox("Fresh Produce / Crop", all_crops)

# Zone selector
all_zones = ["All Zones"] + sorted(list(raw_df["Zone"].dropna().unique()))
selected_zone = st.sidebar.selectbox("Origin Corridor", all_zones)

# Risk Tier selector
all_tiers = ["All Risk Tiers", "CRITICAL", "AT_RISK", "FRESH"]
selected_tier = st.sidebar.selectbox("Spoilage Risk Status", all_tiers)

# Only Breaches Checkbox
only_breaches = st.sidebar.checkbox("🚨 Only Cargo Breaches (>15°C)", value=False)

# Apply filters
df = raw_df.copy()
if selected_crop != "All Produce":
    df = df[df["crop_type"] == selected_crop]
if selected_zone != "All Zones":
    df = df[df["Zone"] == selected_zone]
if selected_tier != "All Risk Tiers":
    df = df[df["risk_tier"] == selected_tier]
if only_breaches:
    df = df[df["temp_breach"]]

# Recalculate KPIs on filtered subset
kpis = ops_engine.calculate_kpis(df)

# Sidebar Quick Actions
st.sidebar.markdown("---")
st.sidebar.markdown("<h4 style='color: #1b4332; margin-bottom: 8px;'>⚡ Executive Actions</h4>", unsafe_allow_html=True)
if st.sidebar.button("📄 Generate Audit PDF", use_container_width=True):
    pdf_file = ops_engine.generate_operational_pdf_report(df, "reports/daily_ops_report.pdf")
    with open(pdf_file, "rb") as f:
        st.sidebar.download_button(
            label="⬇️ Download Executive Audit PDF",
            data=f,
            file_name="FreshOps_Daily_Audit_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# ---------------------------------------------------------
# Executive Hero Banner
# ---------------------------------------------------------
st.markdown("""
<div class="hero-glass-card">
    <div class="hero-badge">🌱 FRESH-SUPPLIES LOGISTICS INTELLIGENCE &bull; KENYA VALUE CHAIN</div>
    <div class="hero-title">FreshOps AI — Executive Cold-Chain Control Room</div>
    <div class="hero-subtitle">Real-time horticultural preservation, thermal exposure analytics, and predictive market diversion for fresh agricultural supply chains.</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# High-Contrast Glassmorphic KPI Metric Grid
# ---------------------------------------------------------
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-glass-card">
        <div class="kpi-label">Active Cargo Fleet</div>
        <div class="kpi-value">{kpis['total_shipments']:,}</div>
        <div class="kpi-sub sub-green">✓ Monitored Batches</div>
    </div>
    <div class="kpi-glass-card">
        <div class="kpi-label">At-Risk Produce</div>
        <div class="kpi-value" style="color: {'#d90429' if kpis['at_risk_count'] > 0 else '#2d6a4f'};">{kpis['at_risk_count']:,}</div>
        <div class="kpi-sub {'sub-red' if kpis['at_risk_count'] > 0 else 'sub-green'}">{'⚠ Urgent Review' if kpis['at_risk_count'] > 0 else '✓ Optimal Condition'}</div>
    </div>
    <div class="kpi-glass-card">
        <div class="kpi-label">Temp Breaches (&gt;15°C)</div>
        <div class="kpi-value" style="color: {'#d90429' if kpis['temp_breaches'] > 0 else '#2d6a4f'};">{kpis['temp_breaches']:,}</div>
        <div class="kpi-sub {'sub-red' if kpis['temp_breaches'] > 0 else 'sub-green'}">{'❄ Thermal Spikes' if kpis['temp_breaches'] > 0 else '✓ Safe Cold-Chain'}</div>
    </div>
    <div class="kpi-glass-card">
        <div class="kpi-label">Severe Delays (&gt;16h)</div>
        <div class="kpi-value" style="color: {'#d97706' if kpis['transit_delays'] > 0 else '#2d6a4f'};">{kpis['transit_delays']:,}</div>
        <div class="kpi-sub sub-orange">Highway Bottlenecks</div>
    </div>
    <div class="kpi-glass-card">
        <div class="kpi-label">Revenue at Risk</div>
        <div class="kpi-value">KES {kpis['revenue_at_risk_kes']:,.0f}</div>
        <div class="kpi-sub sub-red">At Terminal Markets</div>
    </div>
    <div class="kpi-glass-card" style="background: rgba(220, 252, 231, 0.85); border-color: rgba(74, 222, 128, 0.5);">
        <div class="kpi-label" style="color: #1b4332;">Retained via Reroute</div>
        <div class="kpi-value" style="color: #1b4332;">KES {kpis['estimated_salvage_kes']:,.0f}</div>
        <div class="kpi-sub sub-green"><b>+75% Salvage Efficiency</b></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Executive Tabs
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🛰️ Fleet & Cold-Chain Radar",
    "🔄 Dynamic Market Rerouting Simulator",
    "🤖 AI Ops Copilot (Q&A)",
    "📑 Dispatch Alerts & Reports"
])

# ---------------------------------------------------------
# TAB 1: FLEET & COLD-CHAIN RADAR
# ---------------------------------------------------------
with tab1:
    st.markdown("### 📍 Live Fleet Tracking & Cargo Thermal Distribution")

    map_col, chart_col = st.columns([3, 2])

    with map_col:
        # Sample for fast interactive rendering if dataset is large
        plot_df = df.sample(min(800, len(df)), random_state=42) if len(df) > 800 else df

        # Leafy green palette color mapping for risk tiers
        color_map = {
            "CRITICAL": "#d90429",   # Bold alert red
            "AT_RISK": "#e85d04",    # Vibrant amber
            "FRESH": "#2d6a4f"       # Lush forest green
        }

        fig_map = px.scatter(
            plot_df,
            x="longitude",
            y="latitude",
            color="risk_tier",
            color_discrete_map=color_map,
            hover_name="shipment_id",
            hover_data={
                "crop_type": True,
                "Temperature_C": ":.1f",
                "Transit_Duration_Hr": ":.1f",
                "best_market_name": True,
                "risk_tier": True,
                "latitude": False,
                "longitude": False
            },
            title="Produce Transit Corridors & Quality Risk (Kenya)",
            height=440
        )
        fig_map.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(255,255,255,0.7)",
            plot_bgcolor="rgba(240,248,242,0.5)",
            margin=dict(l=10, r=10, t=35, b=10),
            xaxis_title="Longitude (°E)",
            yaxis_title="Latitude (°N/°S)",
            font=dict(family="Plus Jakarta Sans", color="#132a13")
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with chart_col:
        fig_hist = px.histogram(
            df,
            x="Temperature_C",
            color="risk_tier",
            color_discrete_map=color_map,
            nbins=24,
            title="Cargo Thermal Exposure vs 15°C Breach Threshold",
            height=440
        )
        fig_hist.add_vline(x=15.0, line_dash="dash", line_color="#d90429", annotation_text="15°C Breach Limit", annotation_position="top right")
        fig_hist.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(255,255,255,0.7)",
            plot_bgcolor="rgba(240,248,242,0.5)",
            margin=dict(l=10, r=10, t=35, b=10),
            xaxis_title="Cargo Temp (°C)",
            yaxis_title="Truck Batches",
            font=dict(family="Plus Jakarta Sans", color="#132a13")
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("### 🚨 Urgent Attention Queue (Critical Thermal Breaches)")
    urgent_df = df[df["operational_alert"]].sort_values(
        by=["Temperature_C", "loss_value_kes"], ascending=[False, False]
    ).head(12)

    display_cols = [
        "shipment_id", "crop_type", "Zone", "Temperature_C",
        "Transit_Duration_Hr", "risk_tier", "loss_value_kes", "best_market_name"
    ]
    st.dataframe(
        urgent_df[display_cols].rename(columns={
            "shipment_id": "Batch ID",
            "crop_type": "Produce",
            "Temperature_C": "Temp (°C)",
            "Transit_Duration_Hr": "Transit (h)",
            "risk_tier": "Risk Tier",
            "loss_value_kes": "Value at Stake (KES)",
            "best_market_name": "Target Destination"
        }),
        use_container_width=True
    )

# ---------------------------------------------------------
# TAB 2: DYNAMIC MARKET REROUTING SIMULATOR
# ---------------------------------------------------------
with tab2:
    st.markdown("### 🔄 Dynamic Wholesale Market Arbitrage & Spoilage Prevention")
    st.markdown("""
    When cold-chain breaches occur mid-transit, continuing towards distant destinations causes total loss.
    This simulator dynamically identifies the optimal alternative regional wholesale hub in Kenya to **maximize retained revenue**.
    """)

    # Select an at-risk shipment
    sample_candidates = df[df["operational_alert"]]
    if sample_candidates.empty:
        sample_candidates = df

    selected_batch_id = st.selectbox(
        "Select Flagged Shipment Batch for Reroute Analysis:",
        options=sample_candidates["shipment_id"].head(50).tolist()
    )

    selected_row = df[df["shipment_id"] == selected_batch_id].iloc[0]

    # Glass metrics for selected batch
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 20px;">
        <div class="kpi-glass-card">
            <div class="kpi-label">Selected Produce</div>
            <div class="kpi-value" style="font-size: 1.35rem; color: #1b4332;">{selected_row['crop_type']}</div>
        </div>
        <div class="kpi-glass-card">
            <div class="kpi-label">Current Cargo Temp</div>
            <div class="kpi-value" style="font-size: 1.35rem; color: #d90429;">{selected_row['Temperature_C']:.1f} °C</div>
        </div>
        <div class="kpi-glass-card">
            <div class="kpi-label">Current Transit</div>
            <div class="kpi-value" style="font-size: 1.35rem; color: #e85d04;">{selected_row['Transit_Duration_Hr']:.1f} hrs</div>
        </div>
        <div class="kpi-glass-card">
            <div class="kpi-label">Original Destination</div>
            <div class="kpi-value" style="font-size: 1.15rem; color: #2d6a4f;">{selected_row.get('best_market_name', 'Nairobi')[:18]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 🎛️ What-If Scenario Stress Testing")
    what_col1, what_col2 = st.columns(2)
    with what_col1:
        added_delay = st.slider("Simulate Additional Highway Delay (Hours)", 0.0, 8.0, 0.0, 0.5)
    with what_col2:
        cooling_adj = st.slider("Simulate Active Onboard Cooling (°C Reduction)", -5.0, 5.0, 0.0, 0.5)

    simulated_temp = selected_row["Temperature_C"] + cooling_adj
    simulated_hrs = selected_row["Transit_Duration_Hr"] + added_delay

    # Run recommendation algorithm
    recs = ops_engine.recommend_alternative_market(selected_row, market_prices_df, market_dest_df)

    if recs:
        recs_df = pd.DataFrame(recs)
        st.markdown("#### 📊 Wholesale Market Arbitrage Ranking (Kenya)")
        
        top_alt = recs[0]
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(220, 252, 231, 0.9) 0%, rgba(187, 247, 208, 0.8) 100%);
                    border: 1px solid rgba(74, 222, 128, 0.6); border-radius: 14px; padding: 18px 24px; margin-bottom: 20px;">
            <h4 style="margin: 0 0 6px 0; color: #081c15; font-weight: 800;">🎯 Recommended Market Diversion</h4>
            <p style="margin: 0; color: #1b4332; font-size: 1.05rem; line-height: 1.5;">
                Divert batch <b>{selected_batch_id}</b> to <b>{top_alt['market_name']}</b> ({top_alt['region']}). 
                Transit distance: <b>{top_alt['distance_km']} km</b> (~{top_alt['est_transit_hrs']} hrs). 
                Projected Salvageable Revenue: <b style="color: #081c15; font-size: 1.15rem;">KES {top_alt['salvage_revenue_100kg']:,.2f}</b> per 100kg batch!
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.dataframe(
            recs_df[[
                "market_name", "region", "distance_km", "est_transit_hrs",
                "price_per_kg", "gross_revenue_100kg", "salvage_revenue_100kg", "is_current"
            ]].rename(columns={
                "market_name": "Wholesale Market",
                "region": "County / Region",
                "distance_km": "Distance (km)",
                "est_transit_hrs": "Est. Travel (h)",
                "price_per_kg": "Price (KES/kg)",
                "gross_revenue_100kg": "Gross Value (KES)",
                "salvage_revenue_100kg": "Net Salvage Revenue (KES)",
                "is_current": "Original Target"
            }),
            use_container_width=True
        )

        if st.button("🚀 Authorize & Broadcast Market Diversion"):
            st.balloons()
            st.success(f"Market Diversion Order logged! Dispatching updated routing instructions for {top_alt['market_name']}.")

# ---------------------------------------------------------
# TAB 3: AI OPS COPILOT (Q&A)
# ---------------------------------------------------------
with tab3:
    st.markdown("### 🤖 FreshOps AI Copilot — Conversational Operational Assistant")
    st.markdown("Ask natural language questions about fleet health, cold-chain violations, regional bottlenecks, or financial exposure.")

    # Preset prompt buttons
    st.markdown("**Suggested Prompts:**")
    pcol1, pcol2, pcol3, pcol4 = st.columns(4)
    preset_query = None
    if pcol1.button("🚨 Cold-chain breaches"):
        preset_query = "What are the current cold-chain breaches and which crops are affected?"
    if pcol2.button("🍅 Tomato risk analysis"):
        preset_query = "Analyze tomato shipments and tell me our loss exposure."
    if pcol3.button("💰 Revenue salvage"):
        preset_query = "Summarize total revenue at risk and our rerouting salvage potential."
    if pcol4.button("📍 Regional corridor status"):
        preset_query = "Give me an operational breakdown across all regional zones."

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [
            {"role": "assistant", "content": "Hello! I am your FreshOps AI Copilot. Ask me any question about our active shipment telemetry, cargo temperatures, or market diversion strategies."}
        ]

    # Render chat history
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle input
    user_input = st.chat_input("Ask FreshOps Copilot a question...") or preset_query
    if user_input:
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing operational telemetry..."):
                response_data = ops_engine.query_ops_copilot(user_input, df, market_prices_df)
                mode_label = response_data.get("mode", "Operational Engine")
                answer_text = f"*{mode_label}*\n\n" + response_data["answer"]
                st.markdown(answer_text)
                st.session_state["chat_history"].append({"role": "assistant", "content": answer_text})

# ---------------------------------------------------------
# TAB 4: DISPATCH ALERTS & REPORTING
# ---------------------------------------------------------
with tab4:
    st.markdown("### 📑 Automated Incident Alerting & Executive Operations Reporting")
    st.markdown("Generate automated operational audit documents and copy-paste formatted alerts for WhatsApp/SMS dispatch.")

    rcol1, rcol2 = st.columns(2)

    with rcol1:
        st.markdown("""
        <div class="glass-panel">
            <h4 style="color: #081c15; margin-top: 0;">📄 Executive PDF Operational Report</h4>
            <p style="color: #2d6a4f; font-size: 0.95rem;">
                Compiles a formal Daily Cold-Chain Audit Report formatted with:
            </p>
            <ul style="color: #132a13; font-size: 0.9rem; line-height: 1.6;">
                <li>Executive KPI summary grid</li>
                <li>Highest-risk batches needing immediate intervention</li>
                <li>Standard Operating Procedures (SOP) for fleet dispatchers</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Generate Executive PDF Report", key="pdf_btn_tab4"):
            pdf_path = ops_engine.generate_operational_pdf_report(df, "reports/daily_ops_report.pdf")
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download Daily_Ops_Report.pdf",
                    data=f,
                    file_name="FreshOps_Daily_Ops_Report.pdf",
                    mime="application/pdf"
                )

    with rcol2:
        sample_breach = df[df["operational_alert"]].head(1)
        if not sample_breach.empty:
            s = sample_breach.iloc[0]
            alert_sms = (
                f"🚨 [FRESH-SUPPLIES DISPATCH ALERT]\n"
                f"Truck Batch: {s['shipment_id']} | Produce: {s['crop_type']}\n"
                f"CURRENT TEMP: {s['Temperature_C']:.1f}°C (BREACH > 15°C)\n"
                f"Transit Duration: {s['Transit_Duration_Hr']:.1f} hrs\n"
                f"ACTION REQUIRED: Dynamic Diversion Approved.\n"
                f"New Target: {s['best_market_name']} ({s['best_market_region']}).\n"
                f"Dispatch Hotline: +254 700 000 000"
            )
        else:
            alert_sms = "No active breaches to format."

        st.markdown("""
        <div class="glass-panel">
            <h4 style="color: #081c15; margin-top: 0;">📱 Driver Incident Alert Formatter</h4>
            <p style="color: #2d6a4f; font-size: 0.9rem;">Ready-to-transmit SMS / WhatsApp alert for field logistics:</p>
        </div>
        """, unsafe_allow_html=True)
        st.text_area("Alert Text Preview:", value=alert_sms, height=140)

    st.markdown("---")
    st.markdown("### 💾 Export Raw Operational Telemetry")
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Filtered Shipments CSV",
        data=csv_data,
        file_name="freshops_filtered_telemetry.csv",
        mime="text/csv"
    )