import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime

# -------------------------
# CONFIG
# -------------------------
BACKEND = "https://sih-final-crg1.onrender.com"    # your backend URL

st.set_page_config(
    page_title="Cloudburst EWS Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)


# -------------------------
# CUSTOM CSS
# -------------------------
st.markdown("""
<style>

body {
    background-color: #0f1117;
}

.big-title {
    font-size: 42px !important;
    font-weight: 900 !important;
    color: #6bc6ff !important;
    padding-bottom: 10px;
}

.stage-box {
    padding: 15px;
    border-radius: 14px;
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 8px;
}

.stage-1 { background: #1e88e5; color: white; }
.stage-2 { background: #fb8c00; color: white; }
.stage-3 { background: #e53935; color: white; }

.status-card {
    background: rgba(255,255,255,0.04);
    padding: 18px;
    border-radius: 15px;
    margin-bottom: 14px;
}

@keyframes balloonFloat {
    0% { transform: translateY(20px); }
    100% { transform: translateY(-40px); }
}

.aerostat-anim {
    animation: balloonFloat 4s ease-in-out infinite alternate;
}

</style>
""", unsafe_allow_html=True)


# -------------------------
# BACKEND HELPERS
# -------------------------
def fetch_json(url, default=None):
    try:
        r = requests.get(url, timeout=4)
        if r.status_code == 200:
            return r.json()
        return default
    except:
        return default


def get_live_nodes():
    return fetch_json(f"{BACKEND}/api/live_latest", [])


def get_hardware():
    return fetch_json(f"{BACKEND}/api/hardware_output", {})


# -------------------------
# HEADER
# -------------------------
st.markdown("<div class='big-title'>⚡ Cloudburst Early Warning System — Dashboard</div>", unsafe_allow_html=True)


# MAIN LAYOUT
col1, col2 = st.columns([2.4, 1])


# ------------------------------------------------------
# LEFT COLUMN → LIVE NODE TABLE + MAP
# ------------------------------------------------------
with col1:
    st.subheader("📡 Live Node Data")

    live = get_live_nodes()

    if live:
        df = pd.DataFrame(live)
        st.dataframe(df, height=260, use_container_width=True)
    else:
        df = None
        st.warning("Waiting for live node data...")

    # ---------------- MAP ----------------
    if df is not None and "lat" in df.columns:
        st.subheader("🗺 Live Node Map")

        fig = px.scatter_mapbox(
            df,
            lat="lat",
            lon="lon",
            hover_name="node_id",
            zoom=11,
            color="stage",
            size=[20]*len(df),
            color_continuous_scale=["blue", "yellow", "red"]
        )

        fig.update_layout(
            mapbox_style="carto-darkmatter",
            height=430,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)



# ------------------------------------------------------
# RIGHT COLUMN → STATUS + AEROSTAT + DRONE
# ------------------------------------------------------
with col2:

    hardware = get_hardware()

    st.subheader("🚨 System Status")

    if hardware:
        for node, info in hardware.items():
            stage = info.get("stage", 1)
            risk = info.get("risk", 0)
            alert = info.get("alert", "NORMAL")

            sclass = "stage-1" if stage == 1 else "stage-2" if stage == 2 else "stage-3"

            st.markdown(
                f"<div class='stage-box {sclass}'>{node.upper()} — Stage {stage} | Risk {risk} | {alert}</div>",
                unsafe_allow_html=True
            )
    else:
        st.info("No hardware status yet.")

    # ------------------ AEROSTAT -------------------
    st.subheader("🎈 Aerostat Status")
    st.image("assets/aerostat.png", width=200, caption="Aerostat", output_format="PNG")

    st.markdown("""
    <div class="status-card">
    Aerostat will launch automatically when any node reaches Stage 2.
    </div>
    """, unsafe_allow_html=True)

    # ------------------ DRONE -------------------
    st.subheader("🛸 Drone Status")
    st.image("assets/drone.png", width=180, caption="Drone Probe", output_format="PNG")

    st.markdown("""
    <div class="status-card">
    Drone probes deploy in Stage 3 to capture in-cloud microphysics.
    </div>
    """, unsafe_allow_html=True)



# ------------------------------------------------------
# SIGNAL HISTORY
# ------------------------------------------------------
st.subheader("📈 Node Signal History")

if df is not None:

    node_list = df["node_id"].unique().tolist()
    sel = st.selectbox("Select node:", node_list)

    dfn = df[df["node_id"] == sel]

    for col in ["pressure", "humidity", "cloud_env_radar_dbz", "pressure_drop_5"]:
        if col in dfn.columns:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dfn.index, y=dfn[col], mode="lines", name=col))
            fig.update_layout(
                title=f"{col} over time",
                height=280,
                margin=dict(l=30, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No past signals available yet.")

# -------------------------
# AUTO-REFRESH
# -------------------------
st.markdown("""
<script>
setTimeout(function(){window.location.reload();}, 4000);
</script>
""", unsafe_allow_html=True)
