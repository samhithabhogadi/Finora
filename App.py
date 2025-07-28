# finora_budget_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
import yfinance as yf
import os
st.set_page_config(page_title="Student Budget Manager", layout="centered")

 #
st.markdown("""
    <style>
        /* Global styles */
        html, body, [class*="css"], .stApp {
            background-color: #ffffff !important;
            color: #000000 !important;
            font-family: 'Segoe UI', sans-serif;
        }

        /* Sidebar */
        .sidebar .sidebar-content {
            background-color: #ffffff !important;
            color: #000000 !important;
        }

        /* All text elements */
        h1, h2, h3, h4, h5, h6, p, span, div, label, .stMarkdown {
            color: #000000 !important;
            background-color: #ffffff !important;
        }

        /* Buttons */
        .stButton>button {
            background-color: #000000 !important; /* Modern teal color */
            color: #ffffff !important; /* White text for contrast */
            border-radius: 8px;
            border: none !important; /* No border */
            padding: 8px 16px;
        }

        /* Text Input */
        .stTextInput > div > div > input {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #cccccc !important;
            caret-color: #000000 !important; /* Ensures cursor is visible */
        }

        /* Selectbox */
        .stSelectbox > div > div > div > div {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #cccccc !important;
        }
        .stSelectbox > div > div > div > div > div {
            background-color: #ffffff !important;
            color: #000000 !important;
        }

        /* Metrics */
        .stMetric > div > div {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        .stMetricLabel, .stMetricValue {
            background-color: #ffffff !important;
            color: #000000 !important;
        }

        /* DataFrame */
        .stDataFrame {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        .stDataFrame tr, .stDataFrame td, .stDataFrame th {
            background-color: #ffffff !important;
            color: #000000 !important;
        }

        /* Expander */
        .stExpander {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        .stExpander > div > div {
            background-color: #ffffff !important;
            color: #000000 !important;
        }

        /* Charts (if any) */
        .stPlotlyChart, .stLineChart, .stAreaChart, .stBarChart {
            background-color: #ffffff !important;
            color: #000000 !important;
        }

        /* Ensure no residual dark themes */
        * {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Finora - Student Budget Manager", page_icon="💰")

# -------------------- User Login --------------------
if 'username' not in st.session_state:
    username = st.text_input("Enter Username to Start", key="username_input")
    if st.button("Login"):
        st.session_state['username'] = username
        st.experimental_rerun()
    st.stop()
else:
    st.sidebar.success(f"Welcome, {st.session_state['username']}!")
    if st.sidebar.button("Logout"):
        del st.session_state['username']
        st.experimental_rerun()

# -------------------- Data Handling --------------------
if os.path.exists('user_data.csv'):
    st.session_state['data'] = pd.read_csv('user_data.csv', parse_dates=['Date'])
else:
    st.session_state['data'] = pd.DataFrame(columns=['Type', 'Amount', 'Category', 'Date'])

data = st.session_state['data']

# -------------------- Sidebar Navigation --------------------
menu = st.sidebar.radio("Navigation", ["Dashboard", "Add Entry", "Financial Education"])

# -------------------- Add Entry --------------------
if menu == "Add Entry":
    st.subheader("➕ Add Income or Expense")
    entry_type = st.selectbox("Type", ["Income", "Expense"])
    amount = st.number_input("Amount", min_value=0.0, step=10.0)
    category = st.text_input("Category")
    entry_date = st.date_input("Date", value=datetime.today().date())
    if st.button("Add Entry"):
        new_entry = pd.DataFrame([[entry_type, amount, category, pd.to_datetime(entry_date)]],
                                  columns=['Type', 'Amount', 'Category', 'Date'])
        st.session_state['data'] = pd.concat([data, new_entry], ignore_index=True)
        st.session_state['data'].to_csv('user_data.csv', index=False)
        st.success("Entry added and saved successfully!")

# -------------------- Dashboard --------------------
elif menu == "Dashboard":
    st.subheader("📊 Dashboard")
    if data.empty:
        st.info("No data available. Add income and expenses to see dashboard.")
    else:
        data['Month'] = data['Date'].dt.to_period('M')
        current_month = pd.Timestamp.now().to_period('M')
        last_month = current_month - 1

        def get_summary(month):
            df = data[data['Month'] == month]
            income = df[df['Type'] == 'Income']['Amount'].sum()
            expense = df[df['Type'] == 'Expense']['Amount'].sum()
            return income, expense

        income_cur, expense_cur = get_summary(current_month)
        income_last, expense_last = get_summary(last_month)
        balance = income_cur - expense_cur

        col1, col2 = st.columns(2)
        with col1:
            st.metric("💸 Current Month Income", f"₹{income_cur:.2f}")
            st.metric("📉 Current Month Expenses", f"₹{expense_cur:.2f}")
            st.metric("🪙 Balance", f"₹{balance:.2f}")

        with col2:
            st.metric("🗓️ Last Month Income", f"₹{income_last:.2f}")
            st.metric("🔻 Last Month Expenses", f"₹{expense_last:.2f}")
            st.metric("📈 Growth", f"₹{(income_cur - income_last):.2f}")

        st.markdown("### 📌 Monthly Overview")
        summary = data.groupby(['Month', 'Type'])['Amount'].sum().unstack().fillna(0)
        st.line_chart(summary)

        st.markdown("### 🥧 Expense Breakdown")
        expense_data = data[(data['Type'] == 'Expense') & (data['Month'] == current_month)]
        if not expense_data.empty:
            pie_data = expense_data.groupby('Category')['Amount'].sum()
            fig, ax = plt.subplots()
            ax.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%')
            ax.axis('equal')
            st.pyplot(fig)

        st.markdown("### 📋 Full Data")
        st.dataframe(data[['Date', 'Type', 'Category', 'Amount']].sort_values(by='Date', ascending=False))

        st.markdown("### 💡 Investment Suggestions")
        if balance > 500:
            st.success("You have a surplus! Here are personalized investment ideas:")
            st.markdown("""
            **Recommended Allocation:**
            - 💼 SIP (Mutual Fund): ₹{:.0f}
              - Example: Axis Bluechip Fund
            - 🏦 Fixed Deposit (FD): ₹{:.0f}
              - Example: HDFC FD at 7%
            - 📱 Emergency Savings: ₹{:.0f}
              - Use a UPI wallet or recurring deposit
            """.format(balance * 0.5, balance * 0.3, balance * 0.2))
        else:
            st.info("Try to reduce expenses or increase income to have an investable surplus.")

        # -------------------- Gamification --------------------
        st.markdown("### 🏅 Achievements")
        total_income = data[data['Type'] == 'Income']['Amount'].sum()
        total_expense = data[data['Type'] == 'Expense']['Amount'].sum()
        total_saved = total_income - total_expense

        if total_saved >= 1000:
            st.success("💸 Budget Beginner - Saved ₹1,000")
        if total_saved >= 5000:
            st.success("🎯 Smart Saver - Saved ₹5,000")
        if total_saved >= 10000:
            st.success("🏆 Wealth Warrior - Saved ₹10,000")
        if len(data) >= 10:
            st.info("🗂️ Consistency Champ - 10+ entries logged")
        if data['Category'].nunique() >= 5:
            st.info("🎨 Diverse Tracker - 5+ unique categories")

        st.markdown("### 🔥 Logging Streak")
        data['DateOnly'] = data['Date'].dt.date
        unique_days = data['DateOnly'].nunique()
        st.info(f"📆 You've added entries on **{unique_days}** days!")
        if unique_days >= 3:
            st.success("🔥 3-Day Streak!")
        if unique_days >= 7:
            st.success("🚀 1-Week Logging Streak!")
        if unique_days >= 30:
            st.success("🌟 1-Month Consistency Hero!")

        def calculate_xp(data):
            income_entries = data[data['Type'] == 'Income'].shape[0]
            expense_entries = data[data['Type'] == 'Expense'].shape[0]
            xp = (income_entries * 5) + (expense_entries * 3)
            return xp

        xp = calculate_xp(data)
        level = xp // 100 + 1
        next_level_xp = (level * 100) - xp
        st.markdown(f"### 🎮 Level: {level}")
        st.progress((xp % 100) / 100)
        st.caption(f"⭐ {xp} XP - {next_level_xp} XP to next level")

        coins = xp // 10
        st.sidebar.markdown(f"💰 Coins Earned: **{coins}**")
        if coins >= 100:
            st.sidebar.success("🎁 Redeemable: Premium Tip Pack")
        else:
            st.sidebar.info(f"Earn {100 - coins} more coins to unlock rewards!")

# -------------------- Financial Education --------------------
elif menu == "Financial Education":
    st.subheader("📚 Financial Education")
    st.markdown("### 🧠 Tips & Tricks")
    st.markdown("""
    - 🧾 Track your expenses daily to avoid overspending
    - 💳 Avoid high-interest debt like credit cards
    - 💸 Automate savings each month
    - 📈 Start investing early in mutual funds or ETFs
    - 📚 Learn about SIPs, budgeting, and financial goals
    """)

    st.markdown("### 🗞️ Latest Financial News")
    with st.expander("Click to View"):
        st.markdown("- Sensex climbs 300 pts; Nifty above 23,500 ahead of Fed decision")
        st.markdown("- Gold prices drop as dollar strengthens on Fed signals")
        st.markdown("- Mutual Fund SIPs hit record ₹18,000 crore in June 2025")

# -------------------- Upload & Download --------------------
st.sidebar.markdown("### 📂 Data Options")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type="csv")
if uploaded_file:
    st.session_state['data'] = pd.read_csv(uploaded_file, parse_dates=['Date'])
    st.success("Data uploaded successfully!")

csv = st.session_state['data'].to_csv(index=False).encode('utf-8')
st.sidebar.download_button("Download My Data", csv, "my_budget_data.csv", "text/csv")

        st.markdown("- RBI hints at rate cut if inflation remains within target")

    st.markdown("---")
    st.info("We plan to integrate a news API for live updates in future versions!")
