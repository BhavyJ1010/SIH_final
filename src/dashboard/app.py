# ========================================================================
# Cloudburst Early Warning System — Streamlit Dashboard
# Connected to FastAPI backend
# ========================================================================

import streamlit as st
import pandas as pd
import numpy as np
import requests
import pydeck as pdk
import plotly.express as px
from datetime import datetime, timedelta

# ------------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------------

st.set_page_config(
    page_title="Cloudburst EWS Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CHANGE THIS ➜ If deployed, set API_BASE in Streamlit Secrets
API_BASE = st.secrets.get("API_BASE", "http://127.0.0.1:8000")

def api_get(path):
    try:
        r = requests.get(API_BASE + path, timeout=3)
        if r.ok:
            return r.json()
    except:
        return None

def api_post(path, payload):
    try:
        r = requests.post(API_BASE + path, json=payload, timeout=3)
        return r.ok
    except:
        return False

# ------------------------------------------------------------------------
# LOAD DATA FROM FASTAPI
# ------------------------------------------------------------------------

def load_live_latest():
    rows = api_get("/api/live_latest")
    if rows:
        return pd.DataFrame(rows)
    return pd.DataFrame()

def load_predictions():
    preds = api_get("/api/predictions")
    if preds and isinstance(preds, list) and len(preds):
        return preds[-1]
    return []

def load_stage_state():
    return api_get("/api/stage_state") or {}

def load_hw_output():
    return api_get("/api/hardware_output") or {}

# ------------------------------------------------------------------------
# HEADER
# ------------------------------------------------------------------------

st.title("🌩️ Cloudburst Early Warning System — Dashboard")

# ------------------------------------------------------------------------
# SIDEBAR CONTROLS
# ------------------------------------------------------------------------

st.sidebar.header("Settings & Controls")

auto_refresh = st.sidebar.checkbox("Enable Auto Refresh", value=False)
refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 3, 20, 6)

st.sidebar.subheader("Manual Stage Override")
sel_node = st.sidebar.selectbox("Select Node", ["node0","node1","node2","node3","node4"])
sel_stage = st.sidebar.selectbox("Stage", [1,2,3])

if st.sidebar.button("Apply Manual Override"):
    api_post("/api/manual_stage", {sel_node: sel_stage})
    st.sidebar.success(f"Manual override applied: {sel_node} → stage {sel_stage}")

if st.sidebar.button("Clear Override"):
    api_post("/api/manual_stage", {})
    st.sidebar.success("Manual override cleared.")

st.sidebar.markdown("---")

# ------------------------------------------------------------------------
# LOAD LIVE DATA
# ------------------------------------------------------------------------

live_df = load_live_latest()
pred_block = load_predictions()
hw_out = load_hw_output()
stage_state = load_stage_state()

# ------------------------------------------------------------------------
# LAYOUT : LEFT (Map + Table + Charts) / RIGHT (Actions + Forecast)
# ------------------------------------------------------------------------

left, right = st.columns([2,1])

# ------------------------------------------------------------------------
# LEFT PANEL
# ------------------------------------------------------------------------

with left:
    st.subheader("📡 Live Node Data")

    if live_df.empty:
        st.warning("No live data yet. Start generator + predictor.")
    else:
        st.write("Latest parameters (all nodes):")
        st.dataframe(live_df, use_container_width=True)

        # ----------------------
        # INTERACTIVE MAP (PyDeck)
        # ----------------------
        st.subheader("🗺️ Node Map")

        map_data = live_df.copy()
        map_data["latitude"] = map_data["lat"]
        map_data["longitude"] = map_data["lon"]

        # circle radius scaled by risk
        def risk_radius(node):
            for p in pred_block:
                if p["node_id"] == node:
                    return 800 + p["risk_score"] * 20
            return 800

        map_data["radius"] = [risk_radius(n) for n in map_data["node_id"]]

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_data,
            get_position=["longitude", "latitude"],
            get_radius="radius",
            get_color=[0, 200, 0, 160],
            pickable=True
        )

        view_state = pdk.ViewState(
            latitude=map_data["latitude"].mean(),
            longitude=map_data["longitude"].mean(),
            zoom=11,
            pitch=20
        )

        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

        # ----------------------
        # TIMELINE CHARTS
        # ----------------------
        st.subheader("📈 Timeline Signals")

        df_all = api_get("/api/live_latest")
        if df_all:
            df_chart = load_live_latest()  # only latest timestamp
            # Instead: load full live.csv for big charts
            try:
                full = requests.get(API_BASE + "/api/live_latest").json()
            except:
                full = df_chart.to_dict(orient="records")

        node_sel = st.selectbox("Select node for time-series:", ["node0","node1","node2","node3","node4"])

        try:
            big_df = pd.read_csv(str(Path(API_BASE.replace("http://127.0.0.1:8000","")).joinpath("data/live.csv")))
        except:
            big_df = pd.DataFrame()

        if not big_df.empty:
            df_node = big_df[big_df["node_id"] == node_sel].tail(300)
            if "timestamp" in df_node:
                df_node["ts_dt"] = pd.to_datetime(df_node["timestamp"])
                fig = px.line(
                    df_node,
                    x="ts_dt",
                    y=["cloud_env_radar_dbz","pressure","humidity"],
                    title=f"Signal History — {node_sel}"
                )
                st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------------
# RIGHT PANEL
# ------------------------------------------------------------------------

with right:
    st.subheader("🔧 Node Status & Alerts")

    for n in ["node0","node1","node2","node3","node4"]:
        stage = stage_state.get(n, 1)
        alert = hw_out.get(n, {}).get("alert", "NORMAL")

        if alert == "HIGH_RISK":
            st.error(f"{n} → Stage {stage} | ALERT: HIGH RISK")
        elif alert == "WARNING":
            st.warning(f"{n} → Stage {stage} | WARNING")
        else:
            st.success(f"{n} → Stage {stage} | NORMAL")

    st.markdown("---")
    st.subheader("🎈 Aerostat & Drone Simulator")

    sim_node = st.selectbox("Node for simulation:", ["node0","node1","node2","node3","node4"])
    sim_stage = stage_state.get(sim_node, 1)

    # session-state for deployments
    if "aero" not in st.session_state:
        st.session_state.aero = {n: False for n in ["node0","node1","node2","node3","node4"]}
    if "drone" not in st.session_state:
        st.session_state.drone = {n: False for n in ["node0","node1","node2","node3","node4"]}

    # -----------------------
    # Aerostat Button
    # -----------------------
    if sim_stage >= 2 and not st.session_state.aero[sim_node]:
        if st.button("Deploy Aerostat"):
            with st.spinner("Launching aerostat..."):
                for i in range(100):
                    time.sleep(0.01)
            st.session_state.aero[sim_node] = True
            st.success("Aerostat deployed! Sensors activated.")
    elif st.session_state.aero[sim_node]:
        st.info("Aerostat currently deployed.")
        if st.button("Retract Aerostat"):
            st.session_state.aero[sim_node] = False
            st.success("Aerostat retracted.")

    # -----------------------
    # Drone Button
    # -----------------------
    if sim_stage >= 3 and not st.session_state.drone[sim_node]:
        if st.button("Launch Drone Probe"):
            with st.spinner("Launching drone..."):
                for i in range(100):
                    time.sleep(0.01)
            st.session_state.drone[sim_node] = True
            st.success("Drone probe active!")
    elif st.session_state.drone[sim_node]:
        st.info("Drone probe already launched.")
        if st.button("Recall Drone"):
            st.session_state.drone[sim_node] = False
            st.success("Drone recalled.")

    # --------------------------------------------------------------------
    # 2-HOUR FORECAST (if Aerostat deployed)
    # --------------------------------------------------------------------

    st.markdown("---")
    st.subheader("⏳ 2-Hour Cloudburst Risk Forecast")

    if st.session_state.aero[sim_node]:
        st.info("Aerostat sensors active → forecasting enabled.")

        preds = pred_block
        if preds:
            for p in preds:
                if p["node_id"] == sim_node:
                    base_risk = p["risk_score"]

            # simple forecast stub
            times = []
            risks = []
            for i in range(8):
                times.append((datetime.now() + timedelta(minutes=15*(i+1))).strftime("%H:%M"))
                risks.append(min(100, base_risk + i*4 + np.random.normal(0,2)))

            fig2 = px.line(x=times, y=risks, labels={"x":"Time", "y":"Risk (%)"}, title="Forecasted Risk (2 hours)")
            st.plotly_chart(fig2, use_container_width=True)

            # burst estimate
            for i, r in enumerate(risks):
                if r >= 70:
                    st.error(f"⚠️ Cloudburst likely in ~{(i+1)*15} minutes.")
                    break
            else:
                st.success("No cloudburst expected in next 2 hours.")
    else:
        st.warning("Deploy Aerostat for advanced forecasting.")

# ------------------------------------------------------------------------
# AUTO REFRESH
# ------------------------------------------------------------------------

if auto_refresh:
    st.write(f"<meta http-equiv='refresh' content='{refresh_interval}'>", unsafe_allow_html=True)
