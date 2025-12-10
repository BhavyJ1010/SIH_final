import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

BACKEND = "https://sih-final-crg1.onrender.com"   # correct backend

st.set_page_config(page_title="Cloudburst EWS", layout="wide")

# ------------------------------------------------------
# CSS + AEROSTAT ANIMATION
# ------------------------------------------------------
AEROSTAT_IMG = "https://raw.githubusercontent.com/BhavyJ1010/SIH_final_assets/main/aerostat.png"
DRONE_IMG     = "https://raw.githubusercontent.com/BhavyJ1010/SIH_final_assets/main/drone.png"

st.markdown("""
<style>
.title {
    font-size: 40px;
    font-weight: 900;
    color: #4fc3f7;
    margin-bottom: 15px;
}
.stage-box {
    padding: 14px;
    border-radius: 12px;
    font-size: 20px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 12px;
}
.s1 { background:#1e88e5; color:white; }
.s2 { background:#fb8c00; color:white; }
.s3 { background:#e53935; color:white; }

.aero-container {
    width: 100%;
    text-align: center;
    padding-top: 25px;
}
@keyframes drift {
    0%   { transform: translateY(0px); }
    100% { transform: translateY(-35px); }
}
.aero-img {
    animation: drift 4s ease-in-out infinite alternate;
}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------
# API HELPERS
# ------------------------------------------------------
def api(path):
    try:
        r = requests.get(f"{BACKEND}{path}", timeout=5)
        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None


# ------------------------------------------------------
# TITLE
# ------------------------------------------------------
st.markdown("<div class='title'>⚡ Cloudburst Early Warning System</div>", unsafe_allow_html=True)

col1, col2 = st.columns([2.2, 1])


# ------------------------------------------------------
# LEFT SIDE — LIVE NODE DATA
# ------------------------------------------------------
with col1:
    st.subheader("📡 Live Node Data")

    live = api("/api/live_latest")
    if live:
        df = pd.DataFrame(live)
        st.dataframe(df, height=260)

        # Map
        fig = px.scatter_mapbox(
            df,
            lat="lat",
            lon="lon",
            hover_name="node_id",
            color="stage",
            size=[20]*len(df),
            color_continuous_scale=["blue", "yellow", "red"],
            zoom=11
        )
        fig.update_layout(mapbox_style="carto-darkmatter", height=420)
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Waiting for live node data...")


# ------------------------------------------------------
# RIGHT SIDE — STATUS + AEROSTAT
# ------------------------------------------------------
with col2:
    st.subheader("🚨 System Status")

    hw = api("/api/hardware_output")

    if hw:
        for node, info in hw.items():
            stage = info.get("stage", 1)
            risk  = info.get("risk", 0)
            alert = info.get("alert", "NORMAL")
            cls = "s1" if stage == 1 else "s2" if stage == 2 else "s3"

            st.markdown(
                f"<div class='stage-box {cls}'>{node.upper()} — Stage {stage} | {alert}</div>",
                unsafe_allow_html=True,
            )

    # Aerostat
    st.subheader("🎈 Aerostat")
    st.markdown(
        f"<div class='aero-container'><img src='{AEROSTAT_IMG}' width='180' class='aero-img'></div>",
        unsafe_allow_html=True,
    )
    st.info("Deploys automatically in Stage 2.")

    # Drone
    st.subheader("🛸 Drone")
    st.image(DRONE_IMG, width=150)


# ------------------------------------------------------
# TIMELINE CHARTS
# ------------------------------------------------------
st.subheader("📈 Node Signal History")

node_opt = st.selectbox("Select node", ["node0","node1","node2","node3","node4"])

if live:
    df = pd.DataFrame(live)
    node_df = df[df["node_id"] == node_opt]

    graph_cols = ["pressure", "humidity", "cloud_env_radar_dbz", "pressure_drop_5"]

    for col in graph_cols:
        if col in node_df.columns:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(range(len(node_df))),
                y=node_df[col],
                mode="lines",
            ))
            fig.update_layout(title=col, height=300)
            st.plotly_chart(fig, use_container_width=True)

# Auto-refresh every 4 seconds
st.markdown("""
<script>
setTimeout(() => window.location.reload(), 4000);
</script>
""", unsafe_allow_html=True)
