# finora_budget_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
import yfinance as yf
import os

st.set_page_config(page_title="Finora - Student Budget Manager", layout="wide", initial_sidebar_state="expanded")

## Replace the existing st.markdown style block with this
st.markdown(
    """
    <style>
        /* Global background and text */
        html, body, .stApp {
            background-color: #ffffff !important;
            color: #000000 !important;
        }

        /* Fix for widgets input background */
        input, textarea, select {
            background-color: #ffffff !important;
            color: #000000 !important;
        }

        /* Button Styling */
        .stButton > button {
            background-color: #4f8df7;
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
        }

        .stButton > button:hover {
            background-color: #45a049;
        }

        /* Sidebar styling */
        .css-1d391kg {  /* streamlit sidebar container */
            background-color: #ffffff !important;
            color: #000000 !important;
        }

        /* Headings and labels */
        h1, h2, h3, h4, h5, h6, label, p, span, div {
            color: #000000 !important;
        }

        /* Metric cards or custom blocks if any */
        .metric-card {
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            padding: 1rem;
            margin-bottom: 1rem;
        }

        /* DataFrame text */
        .css-1fcb1v8, .css-ffhzg2 {
            color: #000000 !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)
st.title("💰 Finora - Student Budget Manager")
st.markdown("A simple app to track your income and expenses and learn about money management.")

if os.path.exists('user_data.csv'):
    st.session_state['data'] = pd.read_csv('user_data.csv', parse_dates=['Date'])
else:
    st.session_state['data'] = pd.DataFrame(columns=['Type', 'Amount', 'Category', 'Date'])

menu = st.sidebar.radio("Navigation", ["Dashboard", "Add Entry", "Financial Education"])

if menu == "Add Entry":
    st.subheader("➕ Add Income or Expense")
    entry_type = st.selectbox("Type", ["Income", "Expense"])
    amount = st.number_input("Amount", min_value=0.0, step=10.0)
    category = st.text_input("Category")
    entry_date = st.date_input("Date", value=datetime.today().date())
    if st.button("Add Entry"):
        new_entry = pd.DataFrame([[entry_type, amount, category, pd.to_datetime(entry_date)]],
                                  columns=['Type', 'Amount', 'Category', 'Date'])
        st.session_state['data'] = pd.concat([st.session_state['data'], new_entry], ignore_index=True)
        st.session_state['data'].to_csv('user_data.csv', index=False)
        st.success("Entry added and saved successfully!")

elif menu == "Dashboard":
    st.subheader("📊 Dashboard")
    data = st.session_state['data']
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

        col1, col2 = st.columns(2)
        with col1:
            st.metric("💸 Current Month Income", f"₹{income_cur:.2f}")
            st.metric("📉 Current Month Expenses", f"₹{expense_cur:.2f}")
            balance = income_cur - expense_cur
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
              - Example: Axis Bluechip Fund - suitable for long-term growth
            - 🏦 Fixed Deposit (FD): ₹{:.0f}
              - Example: HDFC FD at 7% for 1 year
            - 📱 Emergency Savings (UPI Wallet / RD): ₹{:.0f}
              - Keep liquid funds for small emergencies
            """.format(balance * 0.5, balance * 0.3, balance * 0.2))
        else:
            st.info("Try to reduce expenses or increase income to have an investable surplus.")

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
        st.markdown("- RBI hints at rate cut if inflation remains within target")

    st.markdown("---")
    st.info("We plan to integrate a news API for live updates in future versions!")
