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
# CSS
# -----------------------------
st.markdown("""
<style>
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

/* KPI CARDS */
.kpi-card {
    padding:20px;
    border-radius:12px;
    color:white;
    text-align:center;
    font-size:18px;
    font-weight:bold;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    transition: 0.3s;
}
.kpi-card:hover {
    transform: scale(1.05);
}

.blue { background: linear-gradient(45deg, #2196F3, #21CBF3); }
.red { background: linear-gradient(45deg, #ff4b5c, #ff6f61); }
.green { background: linear-gradient(45deg, #00c853, #64dd17); }

.kpi-value {
    font-size:28px;
    margin-top:10px;
}

/* CHAT */
.user-msg {
    background:#007bff;
    color:white;
    padding:10px 15px;
    border-radius:12px;
    margin:5px 0;
    width: fit-content;
    margin-left:auto;
}
.ai-msg {
    background:#e9ecef;
    padding:10px 15px;
    border-radius:12px;
    margin:5px 0;
    width: fit-content;
    margin-right:auto;
}
</style>
""", unsafe_allow_html=True)

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

df = load_data()

# -----------------------------
# LOCAL AI
# -----------------------------
def local_ai(query, data):
    query = query.lower()

    if len(data) == 0:
        return "No data available."

    total = len(data)
    delayed = [d for d in data if d["delayed"]]
    delayed_count = len(delayed)
    avg_time = int(sum(d["total_time"] for d in data) / total)

    if "delay" in query:
        return f"Out of {total} orders, {delayed_count} are delayed."
    elif "total" in query or "orders" in query:
        return f"There are {total} total orders."
    elif "average" in query or "avg" in query:
        return f"Average processing time is {avg_time} seconds."
    elif "slow" in query:
        slow = max(data, key=lambda x: x["total_time"])
        return f"Slowest order is {slow['case_id']} taking {int(slow['total_time'])} seconds."
    elif "fast" in query:
        fast = min(data, key=lambda x: x["total_time"])
        return f"Fastest order is {fast['case_id']} taking {int(fast['total_time'])} seconds."
    elif "summary" in query:
        return f"Total: {total}, Delayed: {delayed_count}, Avg time: {avg_time}s"
    else:
        return "Ask about delays, totals, average time, fastest or slowest orders."

# -----------------------------
# SIDEBAR
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"

st.sidebar.title("☁️ Cloud Intelligence")

if st.sidebar.button("🏠 Home"):
    st.session_state.page = "Home"
if st.sidebar.button("📊 Dashboard"):
    st.session_state.page = "Dashboard"
if st.sidebar.button("💬 Chatbot"):
    st.session_state.page = "Chatbot"

# -----------------------------
# HEADER
# -----------------------------
st.markdown('<div class="header">☁️ Cloud Intelligence System</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Smart Business Monitoring & AI Insights</div>', unsafe_allow_html=True)

# -----------------------------
# HOME
# -----------------------------
if st.session_state.page == "Home":

    st.subheader("Welcome 👋")

    if df.empty:
        st.warning("No data available")
    else:
        total = len(df)
        delayed = int(df['delayed'].sum())
        avg = int(df['total_time'].mean())

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f'<div class="kpi-card blue">📦 Total Orders<div class="kpi-value">{total}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="kpi-card red">⏳ Delayed<div class="kpi-value">{delayed}</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="kpi-card green">⚡ Avg Time<div class="kpi-value">{avg}</div></div>', unsafe_allow_html=True)

        st.markdown("### 📋 Recent Orders")
        st.dataframe(df.head(10), use_container_width=True)

        fig = px.pie(df, names="delayed", title="Delayed vs On-Time")
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# DASHBOARD
# -----------------------------
elif st.session_state.page == "Dashboard":

    filtered_df = df

    if filtered_df.empty:
        st.warning("No data available")
    else:
        st.subheader("📊 Dashboard Overview")

        total = len(filtered_df)
        delayed = int(filtered_df['delayed'].sum())
        avg = int(filtered_df['total_time'].mean())

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f'<div class="kpi-card blue">📦 Total Orders<div class="kpi-value">{total}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="kpi-card red">⏳ Delayed Orders<div class="kpi-value">{delayed}</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="kpi-card green">⚡ Avg Time<div class="kpi-value">{avg}</div></div>', unsafe_allow_html=True)

        st.markdown("### 📈 Analytics")

        fig1 = px.bar(
            filtered_df['delayed'].value_counts().rename_axis('Delayed').reset_index(name='Count'),
            x='Delayed', y='Count', title="Delay Distribution"
        )
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.histogram(
            filtered_df, x="total_time", nbins=10,
            title="Processing Time Distribution"
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### 📋 Process Data")
        st.dataframe(filtered_df, use_container_width=True)

# -----------------------------
# CHATBOT
# -----------------------------
elif st.session_state.page == "Chatbot":

    st.subheader("💬 AI Assistant")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Ask your question...")

    if st.button("Ask"):
        if user_input:

            try:
                payload = {
                    "query": user_input,
                    "data": df.to_dict(orient="records")
                }

                res = requests.post(GENAI_URL, json=payload)
                result = res.json()

                body = json.loads(result.get("body", "{}"))
                reply = body.get("response")

                if not reply:
                    reply = local_ai(user_input, df.to_dict(orient="records"))

            except:
                reply = local_ai(user_input, df.to_dict(orient="records"))

            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("AI", reply))

    for role, msg in st.session_state.chat_history:
        if role == "You":
            col1, col2 = st.columns([1,2])
            with col2:
                st.markdown(f'<div class="user-msg">{msg}</div>', unsafe_allow_html=True)
        else:
            col1, col2 = st.columns([2,1])
            with col1:
                st.markdown(f'<div class="ai-msg">{msg}</div>', unsafe_allow_html=True)
