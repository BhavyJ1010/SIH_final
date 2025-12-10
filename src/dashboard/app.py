import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import plotly.express as px
import plotly.graph_objects as go

BACKEND_URL = "https://sih-final-h38a.onrender.com"   # <-- UPDATE with your actual URL

st.set_page_config(
    page_title="Cloudburst Early Warning System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# UI THEME
# -------------------------------
st.markdown("""
<style>
.big-title {
    font-size: 38px !important;
    font-weight: 900 !important;
    color: #4fc3f7 !important;
}
.stage-box {
    padding: 18px;
    border-radius: 12px;
    text-align: center;
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 12px;
}
.stage-1 { background-color: #1e88e5; color: white; }
.stage-2 { background-color: #fb8c00; color: white; }
.stage-3 { background-color: #e53935; color: white; }
.node-icon {
    background-color: rgba(255,255,255,0.1);
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Aerostat Animation
# -------------------------------
st.markdown("""
<style>
@keyframes floatUp {
  0%   { transform: translateY(40px); }
  100% { transform: translateY(-80px); }
}
.float-balloon {
  animation: floatUp 6s ease-in-out infinite alternate;
}
</style>
""", unsafe_allow_html=True)

BALLOON_ICON = """
<img src="https://i.imgur.com/ol9kdFM.png" width="180" class="float-balloon">
"""

DRONE_ICON = """
<img src="https://i.imgur.com/jrE7aDn.png" width="160">
"""


# -------------------------------
# Helper — Read Backend
# -------------------------------
def get_predictions():
    try:
        r = requests.get(f"{BACKEND_URL}/hardware-output")
        if r.status_code == 200:
            return r.json()
        return {}
    except:
        return {}

def get_live_nodes():
    try:
        r = requests.get(f"{BACKEND_URL}/live-nodes")
        if r.status_code == 200:
            return pd.DataFrame(r.json())
        return pd.DataFrame()
    except:
        return pd.DataFrame()


# -------------------------------
# HEADER
# -------------------------------
st.markdown("<div class='big-title'>⚡ Cloudburst Early Warning System — Dashboard</div>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

# -------------------------------
# COLUMN 1 — LIVE NODE TABLE + MAP
# -------------------------------
with col1:
    st.subheader("📡 Live Node Data")
    df = get_live_nodes()

    if not df.empty:
        st.dataframe(df, height=260)
    else:
        st.warning("Waiting for data...")

    # ---------------- Map ---------------
    if not df.empty:
        fig = px.scatter_mapbox(
            df,
            lat="lat",
            lon="lon",
            color="stage",
            size=[18]*len(df),
            hover_name="node_id",
            zoom=11,
            color_continuous_scale=["blue", "yellow", "red"]
        )
        fig.update_layout(
            mapbox_style="carto-darkmatter",
            height=430,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.subheader("🗺️ Live Node Location Map")
        st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# COLUMN 2 — STAGE INDICATORS + AEROSTAT CONTROL
# -------------------------------
with col2:
    st.subheader("🚨 System Status")

    predictions = get_predictions()

    if predictions:
        for node, info in predictions.items():
            stage = info["stage"]
            risk = info["risk"]
            alert = info["alert"]

            stage_class = "stage-1" if stage == 1 else "stage-2" if stage == 2 else "stage-3"

            st.markdown(
                f"""
                <div class="stage-box {stage_class}">
                    {node.upper()} — Stage {stage} | Risk: {risk} | {alert}
                </div>
                """,
                unsafe_allow_html=True
            )

    # Aerostat section
    st.subheader("🎈 Aerostat Status")
    st.markdown(BALLOON_ICON, unsafe_allow_html=True)

    st.info("Aerostat will launch automatically in Stage 2.")

    # Drone section
    st.subheader("🛸 Drone Status")
    st.markdown(DRONE_ICON, unsafe_allow_html=True)

# -------------------------------
# TIMELINE CHARTS
# -------------------------------
st.subheader("📈 Node Signal History")

node_selected = st.selectbox("Choose node", ["node0", "node1", "node2", "node3", "node4"])

if not df.empty:
    df_node = df[df["node_id"] == node_selected]

    if not df_node.empty:
        for col in ["pressure", "humidity", "cloud_env_radar_dbz", "pressure_drop_5"]:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_node.index, y=df_node[col], mode="lines", name=col))
            fig.update_layout(title=f"{col} over time", height=300)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data yet.")

# Auto-refresh (every 3 seconds)
st.markdown("""
<script>
setTimeout(function(){window.location.reload();}, 3000);
</script>
""", unsafe_allow_html=True)
