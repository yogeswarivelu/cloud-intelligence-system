import streamlit as st
import requests
import pandas as pd
import json
import plotly.express as px

# -----------------------------
# CONFIG
# -----------------------------
API_URL = "https://px6azke1wa.execute-api.ap-south-1.amazonaws.com/prod/process"
GENAI_URL = "https://px6azke1wa.execute-api.ap-south-1.amazonaws.com/prod/genai"

st.set_page_config(page_title="Cloud Intelligence", layout="wide")

# -----------------------------
# PREMIUM CSS
# -----------------------------
st.markdown("""
<style>
body {
    background-color:#f4f7fb;
}
.header {
    background: linear-gradient(90deg, #4facfe, #00f2fe);
    padding:20px;
    border-radius:12px;
    text-align:center;
    color:white;
    font-size:40px;
    font-weight:bold;
}
.subtitle {
    text-align:center;
    margin-bottom:20px;
    color:gray;
}
.kpi {
    padding:20px;
    border-radius:12px;
    color:white;
    text-align:center;
    font-size:18px;
}
.blue {background:#007bff;}
.red {background:#dc3545;}
.green {background:#28a745;}
.user-msg {
    background:#007bff;
    color:white;
    padding:10px;
    border-radius:10px;
    margin:5px;
    text-align:right;
}
.ai-msg {
    background:#e9ecef;
    padding:10px;
    border-radius:10px;
    margin:5px;
}
.chat-center {
    display:flex;
    justify-content:center;
}
.chat-box {
    width:60%;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOGIN SYSTEM
# -----------------------------
USER_CREDENTIALS = {"admin": "1234"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "Home"

def login():
    st.markdown("<h2 style='text-align:center;'>🔐 Login</h2>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")

def logout():
    st.session_state.logged_in = False
    st.rerun()

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    try:
        res = requests.get(API_URL)
        return pd.DataFrame(res.json())
    except:
        return pd.DataFrame()

# -----------------------------
# MAIN APP
# -----------------------------
def main_app():
    df = load_data()

    # -----------------------------
    # SIDEBAR
    # -----------------------------
    st.sidebar.markdown("<h2 style='text-align:center;'>☁️ Cloud Intelligence</h2>", unsafe_allow_html=True)

    # Navigation
    st.sidebar.markdown("### 🔹 Navigation")
    if st.sidebar.button("🏠 Home"):
        st.session_state.page = "Home"
    if st.sidebar.button("📊 Dashboard"):
        st.session_state.page = "Dashboard"
    if st.sidebar.button("💬 Chatbot"):
        st.session_state.page = "Chatbot"

    st.sidebar.markdown("---")

    # Filters
    st.sidebar.markdown("### 🔹 Filters")
    if not df.empty:
        delayed_only = st.sidebar.checkbox("Show only delayed orders")
        min_time, max_time = int(df['total_time'].min()), int(df['total_time'].max())
        time_range = st.sidebar.slider("Processing time range", min_time, max_time, (min_time, max_time))
    else:
        delayed_only = False
        time_range = (0, 1000)

    st.sidebar.markdown("---")

    # Quick KPIs
    st.sidebar.markdown("### 🔹 Quick Stats")
    if not df.empty:
        st.sidebar.metric("Total Orders", len(df))
        st.sidebar.metric("Delayed Orders", int(df['delayed'].sum()))
        st.sidebar.metric("Avg Processing Time", int(df['total_time'].mean()))

    st.sidebar.markdown("---")

    # Logout
    st.sidebar.button("🚪 Logout", on_click=logout)

    # -----------------------------
    # HEADER
    # -----------------------------
    st.markdown('<div class="header">☁️ Cloud Intelligence System</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Smart Business Monitoring & AI Insights</div>', unsafe_allow_html=True)

    # -----------------------------
    # FILTER DATA
    # -----------------------------
    if not df.empty:
        filtered_df = df[
            (df['total_time'] >= time_range[0]) & 
            (df['total_time'] <= time_range[1])
        ]
        if delayed_only:
            filtered_df = filtered_df[filtered_df['delayed'] == 1]
    else:
        filtered_df = pd.DataFrame()

    # -----------------------------
    # HOME PAGE
    # -----------------------------
    if st.session_state.page == "Home":
        st.subheader("Welcome 👋")
        if filtered_df.empty:
            st.warning("No data available")
            return

        c1, c2, c3 = st.columns(3)
        total = len(filtered_df)
        delayed = int(filtered_df['delayed'].sum())
        avg = int(filtered_df['total_time'].mean())

        c1.metric("📦 Orders", total)
        c2.metric("⏳ Delays", delayed)
        c3.metric("⚡ Avg Time", avg)

        st.markdown("### ⚡ Quick Insights")
        if delayed > 0:
            st.error(f"{delayed} orders are delayed. Immediate attention needed!")
        else:
            st.success("All orders are on time.")

        st.markdown("### 📋 Recent Orders")
        st.dataframe(filtered_df.head(10), use_container_width=True)

        st.markdown("### 📊 Quick View")
        fig = px.pie(filtered_df, names="delayed", title="Delayed vs On-Time")
        st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # DASHBOARD
    # -----------------------------
    elif st.session_state.page == "Dashboard":
        if filtered_df.empty:
            st.warning("No data available")
            return

        total = len(filtered_df)
        delayed = int(filtered_df['delayed'].sum())
        avg = int(filtered_df['total_time'].mean())

        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="kpi blue"><h2>{total}</h2>Total Orders</div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi red"><h2>{delayed}</h2>Delayed</div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="kpi green"><h2>{avg}</h2>Avg Time</div>', unsafe_allow_html=True)

        fig1 = px.bar(filtered_df['delayed'].value_counts(), title="Delay Distribution")
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.histogram(filtered_df, x="total_time", title="Processing Time")
        st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(filtered_df, use_container_width=True)

    # -----------------------------
    # CHATBOT
    # -----------------------------
    elif st.session_state.page == "Chatbot":
        st.subheader("💬 AI Assistant")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        st.markdown('<div class="chat-center"><div class="chat-box">', unsafe_allow_html=True)
        user_input = st.text_input("Ask your question...")
        if st.button("Ask"):
            if user_input:
                payload = {
                    "query": user_input,
                    "data": filtered_df.to_dict(orient="records")
                }
                try:
                    res = requests.post(GENAI_URL, json=payload)
                    result = res.json()
                    body = json.loads(result.get("body", "{}"))
                    reply = body.get("response", "No response")
                except:
                    reply = "Error connecting to AI."

                st.session_state.chat_history.append(("You", user_input))
                st.session_state.chat_history.append(("AI", reply))
        st.markdown('</div></div>', unsafe_allow_html=True)

        for role, msg in st.session_state.chat_history:
            if role == "You":
                st.markdown(f'<div class="user-msg">{msg}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ai-msg">{msg}</div>', unsafe_allow_html=True)

# -----------------------------
# FLOW
# -----------------------------
if not st.session_state.logged_in:
    login()
else:
    main_app()
