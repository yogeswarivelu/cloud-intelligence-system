import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import json

# -----------------------------
# CONFIG
# -----------------------------
API_URL = "https://px6azke1wa.execute-api.ap-south-1.amazonaws.com/prod/process"
GENAI_URL = "https://px6azke1wa.execute-api.ap-south-1.amazonaws.com/prod/genai"

st.set_page_config(page_title="Cloud Intelligence", layout="wide")

# -----------------------------
# CUSTOM CSS (UI IMPROVEMENT)
# -----------------------------
st.markdown("""
<style>
.main-title {
    font-size:36px;
    font-weight:bold;
    text-align:center;
    margin-bottom:20px;
}
.card {
    padding:20px;
    border-radius:12px;
    background-color:#f0f2f6;
    text-align:center;
}
.stButton>button {
    width:100%;
    border-radius:8px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOGIN SYSTEM
# -----------------------------
USER_CREDENTIALS = {
    "admin": "1234",
    "user": "abcd"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.logged_in = True
            st.success("Login successful!")
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
        response = requests.get(API_URL)
        data = response.json()
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()

# -----------------------------
# MAIN APP
# -----------------------------
def main_app():

    df = load_data()

    st.markdown('<p class="main-title">📊 Cloud Intelligent Business Dashboard</p>', unsafe_allow_html=True)

    # Logout button
    st.sidebar.button("🚪 Logout", on_click=logout)

    # Sidebar filters
    st.sidebar.title("🔎 Filters")

    if not df.empty:
        min_time = st.sidebar.slider("Minimum Processing Time", 0, int(df['total_time'].max()), 0)
    else:
        min_time = 0

    show_delayed_only = st.sidebar.checkbox("Show Only Delayed Orders")

    filtered_df = df.copy()

    if not df.empty:
        filtered_df = filtered_df[filtered_df['total_time'] >= min_time]

        if show_delayed_only:
            filtered_df = filtered_df[filtered_df['delayed'] == True]

    # Tabs
    tab1, tab2, tab3 = st.tabs(["🏠 Home", "📊 Dashboard", "💬 Chatbot"])

    # -----------------------------
    # HOME
    # -----------------------------
    with tab1:
        st.subheader("🚀 Smart Business Monitoring")

        col1, col2, col3 = st.columns(3)

        col1.markdown('<div class="card">⏱️<br>Detect Delays</div>', unsafe_allow_html=True)
        col2.markdown('<div class="card">📉<br>Bottlenecks</div>', unsafe_allow_html=True)
        col3.markdown('<div class="card">🤖<br>AI Insights</div>', unsafe_allow_html=True)

        st.info("Built using AWS + Process Mining + AI")

    # -----------------------------
    # DASHBOARD
    # -----------------------------
    with tab2:

        st.subheader("📌 Summary")

        col1, col2, col3 = st.columns(3)

        total_orders = len(filtered_df)
        delayed_orders = int(filtered_df['delayed'].sum()) if not filtered_df.empty else 0
        avg_time = int(filtered_df['total_time'].mean()) if not filtered_df.empty else 0

        col1.markdown(f'<div class="card">📦<br><b>{total_orders}</b><br>Total Orders</div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="card">⏳<br><b>{delayed_orders}</b><br>Delayed</div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="card">⚡<br><b>{avg_time}</b><br>Avg Time</div>', unsafe_allow_html=True)

        st.subheader("📊 Analytics")

        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots()
            filtered_df['delayed'].value_counts().plot(kind='bar', ax=ax)
            ax.set_title("Delay Distribution")
            st.pyplot(fig)

        with col2:
            fig2, ax2 = plt.subplots()
            ax2.hist(filtered_df['total_time'], bins=10)
            ax2.set_title("Processing Time")
            st.pyplot(fig2)

        st.subheader("📋 Data")
        st.dataframe(filtered_df, use_container_width=True)

    # -----------------------------
    # CHATBOT
    # -----------------------------
    with tab3:

        st.subheader("💬 Ask AI")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        user_input = st.text_input("Ask something")

        if st.button("Ask") and user_input:
            try:
                payload = {
                    "query": user_input,
                    "data": df.to_dict(orient="records")
                }

                response = requests.post(GENAI_URL, json=payload)
                result = response.json()

                body = json.loads(result.get("body", "{}"))
                reply = body.get("response", "No response")

                st.session_state.chat_history.append(("You", user_input))
                st.session_state.chat_history.append(("AI", reply))

            except Exception as e:
                st.error(f"Error: {e}")

        for role, msg in st.session_state.chat_history:
            if role == "You":
                st.markdown(f"🧑 **You:** {msg}")
            else:
                st.markdown(f"🤖 **AI:** {msg}")

# -----------------------------
# APP FLOW
# -----------------------------
if not st.session_state.logged_in:
    login()
else:
    main_app()
