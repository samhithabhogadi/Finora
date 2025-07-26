# finora_budget_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
import yfinance as yf
import os
import hashlib
import plotly.express as px


# ----------- Helper Functions -----------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists("users.csv"):
        pd.DataFrame(columns=["username", "password"]).to_csv("users.csv", index=False)
    return pd.read_csv("users.csv")

def save_user(username, password_hash):
    users = load_users()
    users.loc[len(users.index)] = [username, password_hash]
    users.to_csv("users.csv", index=False)

def load_transactions(username):
    file_name = f"{username}_transactions.csv"
    if not os.path.exists(file_name):
        pd.DataFrame(columns=["date", "description", "amount", "type"]).to_csv(file_name, index=False)
    return pd.read_csv(file_name)

def save_transaction(username, date, description, amount, trans_type):
    transactions = load_transactions(username)
    transactions.loc[len(transactions.index)] = [date, description, amount, trans_type]
    transactions.to_csv(f"{username}_transactions.csv", index=False)

# ----------- Session Initialization -----------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "password_hash" not in st.session_state:
    st.session_state.password_hash = ""

# ----------- Page Functions -----------
def home():
    st.title("Welcome")
    st.write("A simple app to track your income and expenses and learn about money management.")
    st.info("Use the navigation bar to log in or sign up.")

def login_page():
    st.title("Login")
    login_username = st.text_input("Username", value=st.session_state.username, key="login_username")
    login_password = st.text_input("Password", type="password", value="", key="login_password")
    if st.button("Login", key="login_button"):
        users = load_users()
        pw_hash = hash_password(login_password)
        if ((users["username"] == login_username) & (users["password"] == pw_hash)).any():
            st.session_state.authenticated = True
            st.session_state.username = login_username
            st.session_state.password_hash = pw_hash
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("Incorrect username or password.")

def signup_page():
    st.title("Sign Up")
    signup_username = st.text_input("Choose a Username", key="signup_username")
    signup_password = st.text_input("Choose a Password", type="password", key="signup_password")
    if st.button("Create Account", key="signup_button"):
        users = load_users()
        if signup_username in users["username"].values:
            st.warning("Username already exists.")
        else:
            pw_hash = hash_password(signup_password)
            save_user(signup_username, pw_hash)
            st.success("Signup successful! Logging you in...")
            st.session_state.authenticated = True
            st.session_state.username = signup_username
            st.session_state.password_hash = pw_hash
            st.session_state.page = "dashboard"
            st.rerun()

def dashboard():
    st.title(f"Finora Dashboard - Welcome, {st.session_state.username}!")
    st.markdown("Track your income and expenses below.")
    
    # Transaction Input Form
    st.subheader("Add Transaction")
    with st.form(key="transaction_form"):
        date_input = st.date_input("Date", value=date.today())
        description = st.text_input("Description")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        trans_type = st.selectbox("Type", ["Income", "Expense"])
        submit = st.form_submit_button("Add Transaction")
    
    if submit:
        save_transaction(st.session_state.username, date_input, description, amount, trans_type)
        st.success("Transaction added!")
    
    # Display Transactions
    st.subheader("Your Transactions")
    transactions = load_transactions(st.session_state.username)
    if not transactions.empty:
        st.dataframe(transactions)
        
        # Calculate Summary
        total_income = transactions[transactions["type"] == "Income"]["amount"].sum()
        total_expense = transactions[transactions["type"] == "Expense"]["amount"].sum()
        balance = total_income - total_expense
        st.write(f"**Total Income**: ${total_income:.2f}")
        st.write(f"**Total Expenses**: ${total_expense:.2f}")
        st.write(f"**Balance**: ${balance:.2f}")
        
        # Spending by Type Chart
        chart_data = transactions.groupby("type")["amount"].sum().reset_index()
        if not chart_data.empty:
            st.subheader("Spending Summary")
            fig = px.pie(
                chart_data,
                values="amount",
                names="type",
                title="Income vs Expenses",
                color_discrete_sequence=["#36A2EB", "#FF6384"]
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No transactions yet. Add one above!")

# ----------- Navigation Bar -----------
nav_options = ["Home", "Login", "Sign Up"] if not st.session_state.authenticated else ["Dashboard", "Logout"]
selected_page = st.sidebar.selectbox("Navigate", nav_options)

# ----------- App Router -----------
if selected_page == "Logout":
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.password_hash = ""
    st.session_state.page = "home"
    st.rerun()
elif selected_page == "Home":
    st.session_state.page = "home"
    home()
elif selected_page == "Login":
    st.session_state.page = "login"
    login_page()
elif selected_page == "Sign Up":
    st.session_state.page = "signup"
    signup_page()
elif selected_page == "Dashboard":
    if st.session_state.authenticated:
        st.session_state.page = "dashboard"
        dashboard()
    else:
        st.session_state.page = "login"
        login_page()

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
