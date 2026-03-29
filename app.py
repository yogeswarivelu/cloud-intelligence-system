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

st.set_page_config(page_title="Process Mining Dashboard", layout="wide")

# -----------------------------
# TITLE
# -----------------------------
st.title("📊 Cloud Intelligent Business Dashboard")

# -----------------------------
# LOAD DATA (FINAL FIX - HANDLES ALL CASES)
# -----------------------------
@st.cache_data
def load_data():
    try:
        # Try GET first
        response = requests.get(API_URL)

        if response.status_code != 200:
            # fallback to POST
            response = requests.post(API_URL, json={})

        raw = response.text
        data = json.loads(raw)

        # Case 1: direct list
        if isinstance(data, list):
            return pd.DataFrame(data)

        # Case 2: wrapped response
        if isinstance(data, dict):
            body = data.get("body")

            if isinstance(body, str):
                return pd.DataFrame(json.loads(body))
            elif isinstance(body, list):
                return pd.DataFrame(body)

        return pd.DataFrame()

    except Exception as e:
        st.error(f"API Error: {e}")
        return pd.DataFrame()

df = load_data()

# -----------------------------
# STATUS
# -----------------------------
if df.empty:
    st.warning("⚠️ No data loaded from API")
else:
    st.success("✅ Data loaded successfully")

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("🔎 Filters")

if not df.empty:
    min_time = st.sidebar.slider(
        "Minimum Processing Time",
        0,
        int(df['total_time'].max()),
        0
    )
else:
    min_time = 0

show_delayed_only = st.sidebar.checkbox("Show Only Delayed Orders")

filtered_df = df.copy()

if not df.empty:
    filtered_df = filtered_df[filtered_df['total_time'] >= min_time]

    if show_delayed_only:
        filtered_df = filtered_df[filtered_df['delayed'] == True]

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3 = st.tabs(["🏠 Home", "📊 Dashboard", "💬 Chatbot"])

# -----------------------------
# HOME
# -----------------------------
with tab1:
    st.subheader("🚀 Smart Business Monitoring")
    st.write("Detect delays, bottlenecks and get AI insights.")

# -----------------------------
# DASHBOARD
# -----------------------------
with tab2:

    st.subheader("📌 Summary")

    col1, col2, col3 = st.columns(3)

    total_orders = len(filtered_df)
    delayed_orders = int(filtered_df['delayed'].sum()) if not filtered_df.empty else 0
    avg_time = int(filtered_df['total_time'].mean()) if not filtered_df.empty else 0

    col1.metric("Total Orders", total_orders)
    col2.metric("Delayed Orders", delayed_orders)
    col3.metric("Avg Time", avg_time)

    st.subheader("📊 Analytics")

    col1, col2 = st.columns(2)

    # Delay Graph
    with col1:
        fig, ax = plt.subplots()
        if not filtered_df.empty:
            filtered_df['delayed'].value_counts().plot(kind='bar', ax=ax)
        ax.set_title("Delay Distribution")
        st.pyplot(fig)

    # Time Graph
    with col2:
        fig2, ax2 = plt.subplots()
        if not filtered_df.empty:
            ax2.hist(filtered_df['total_time'], bins=10)
        ax2.set_title("Processing Time")
        st.pyplot(fig2)

    st.subheader("📋 Data")
    st.dataframe(filtered_df, use_container_width=True)

# -----------------------------
# CHATBOT (FINAL WORKING)
# -----------------------------
with tab3:

    st.subheader("💬 Ask AI")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Ask something (e.g., delayed orders, average time)")

    if st.button("Ask") and user_input:
        try:
            if df.empty:
                st.warning("⚠️ No data available")
            else:
                payload = {
                    "query": user_input,
                    "data": df.to_dict(orient="records")
                }

                response = requests.post(GENAI_URL, json=payload)
                result = response.json()

                # Handle both formats
                if isinstance(result, dict) and "body" in result:
                    body = result["body"]
                    if isinstance(body, str):
                        body = json.loads(body)
                else:
                    body = result

                reply = body.get("response", "No response from AI")

                st.session_state.chat_history.append(("You", user_input))
                st.session_state.chat_history.append(("AI", reply))

        except Exception as e:
            st.error(f"Error: {e}")

    # Show chat
    for role, msg in st.session_state.chat_history:
        if role == "You":
            st.markdown(f"🧑 **You:** {msg}")
        else:
            st.markdown(f"🤖 **AI:** {msg}")
