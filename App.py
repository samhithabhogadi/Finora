# finora_budget_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
import yfinance as yf
import os
st.set_page_config(page_title="Student Budget Manager", layout="centered")

# Initialize session state for user login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''

# File paths for user credentials and data
CREDENTIAL_FILE = "credentials.csv"

# Load or create credentials file
if not os.path.exists(CREDENTIAL_FILE):
    pd.DataFrame(columns=['Username', 'Password']).to_csv(CREDENTIAL_FILE, index=False)

# Navigation
if not st.session_state['logged_in']:
    auth_menu = st.sidebar.radio("Login System", ["Sign In", "Sign Up"])
else:
    menu = st.sidebar.selectbox("Navigate", ["Dashboard", "Add Entry", "Logout"])

# Sign Up
if not st.session_state['logged_in'] and auth_menu == "Sign Up":
    st.subheader("✏️ Sign Up")
    new_user = st.text_input("Choose a Username")
    new_password = st.text_input("Choose a Password", type='password')
    if st.button("Create Account"):
        credentials = pd.read_csv(CREDENTIAL_FILE)
        if new_user in credentials['Username'].values:
            st.warning("🚫 Username already exists. Try another one.")
        else:
            new_cred = pd.DataFrame([{'Username': new_user, 'Password': new_password}])
            credentials = pd.concat([credentials, new_cred], ignore_index=True)
            credentials.to_csv(CREDENTIAL_FILE, index=False)
            pd.DataFrame(columns=['Date', 'Type', 'Amount', 'Category', 'Notes']).to_csv(f"data_{new_user}.csv", index=False)
            st.success("✅ Account created! Please sign in.")

# Sign In
if not st.session_state['logged_in'] and auth_menu == "Sign In":
    st.subheader("🔐 Sign In")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Sign In"):
        credentials = pd.read_csv(CREDENTIAL_FILE)
        if ((credentials['Username'] == username) & (credentials['Password'] == password)).any():
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.success(f"✅ Welcome, {username}!")
            st.experimental_rerun()
        else:
            st.error("❌ Incorrect Username or Password")

# Logout
if st.session_state['logged_in'] and menu == "Logout":
    st.session_state['logged_in'] = False
    st.session_state['username'] = ''
    st.success("🚪 Logged out successfully!")
    st.experimental_rerun()

# After login
if st.session_state['logged_in']:
    st.title("📊 Student Budget Manager")

    DATA_FILE = f"data_{st.session_state['username']}.csv"
    if not os.path.exists(DATA_FILE):
        pd.DataFrame(columns=['Date', 'Type', 'Amount', 'Category', 'Notes']).to_csv(DATA_FILE, index=False)

    data = pd.read_csv(DATA_FILE)

    if menu == "Add Entry":
        st.subheader("➕ Add Income or Expense")
        entry_date = st.date_input("Date", value=datetime.date.today())
        entry_type = st.radio("Type", ["Income", "Expense"])
        entry_amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        entry_category = st.text_input("Category")
        entry_notes = st.text_area("Notes")
        if st.button("Save Entry"):
            new_entry = pd.DataFrame({
                'Date': [entry_date],
                'Type': [entry_type],
                'Amount': [entry_amount],
                'Category': [entry_category],
                'Notes': [entry_notes]
            })
            data = pd.concat([data, new_entry], ignore_index=True)
            data.to_csv(DATA_FILE, index=False)
            st.success("✅ Entry saved!")

    elif menu == "Dashboard":
        st.header("📊 Dashboard")

        if 'monthly_budget' not in st.session_state:
            st.session_state['monthly_budget'] = 0.0
        budget = st.number_input("Set Monthly Budget (₹)", value=st.session_state['monthly_budget'])
        st.session_state['monthly_budget'] = budget

        if data.empty:
            st.info("👤 No data yet. Start by adding your income or expenses.")
        else:
            data['Date'] = pd.to_datetime(data['Date'])
            data['Month'] = data['Date'].dt.to_period('M')
            income_total = data[data['Type'] == 'Income']['Amount'].sum()
            expense_total = data[data['Type'] == 'Expense']['Amount'].sum()
            current_month = pd.Timestamp.today().to_period('M')
            this_month_data = data[data['Month'] == current_month]
            income_cur = this_month_data[this_month_data['Type'] == 'Income']['Amount'].sum()
            expense_cur = this_month_data[this_month_data['Type'] == 'Expense']['Amount'].sum()

            if budget and expense_cur > budget:
                st.error("⚠️ You have exceeded your budget!")
            elif budget and expense_cur > 0.9 * budget:
                st.warning("🚨 You're about to reach your monthly budget limit.")

            st.metric("💰 Total Income", f"₹{income_total:.2f}")
            st.metric("💸 Total Expenses", f"₹{expense_total:.2f}")
            st.metric("📉 Budget Remaining", f"₹{budget - expense_cur:.2f}")

            data['Savings'] = data.apply(lambda row: row['Amount'] if row['Type'] == 'Income' else -row['Amount'], axis=1)
            monthly_savings = data.groupby('Month')['Savings'].sum()
            st.subheader("📈 Monthly Savings")
            st.bar_chart(monthly_savings)

        st.subheader("📊 Stock Watchlist")
        symbols = st.text_input("Enter comma-separated tickers (e.g. AAPL, INFY.NS)", value="AAPL,INFY.NS")
        tickers = [s.strip() for s in symbols.split(",") if s.strip()]
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                price = stock.history(period="1d")['Close'].iloc[-1]
                st.metric(f"{ticker}", f"₹{price:.2f}")
            except:
                st.warning(f"⚠️ Could not fetch data for {ticker}")
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
