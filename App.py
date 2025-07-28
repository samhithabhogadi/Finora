# finora_budget_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
import yfinance as yf
import os
import random
from passlib.hash import pbkdf2_sha256

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



# Set page configuration
st.set_page_config(page_title="Finora - Student Budget Manager", page_icon="💰")

# -------------------- User Authentication --------------------
def load_users():
    if os.path.exists('users.csv'):
        return pd.read_csv('users.csv')
    return pd.DataFrame(columns=['Username', 'Password'])

def save_user(username, password):
    users = load_users()
    hashed_password = pbkdf2_sha256.hash(password)
    new_user = pd.DataFrame([[username, hashed_password]], columns=['Username', 'Password'])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_csv('users.csv', index=False)

def verify_user(username, password):
    users = load_users()
    if username in users['Username'].values:
        stored_hash = users[users['Username'] == username]['Password'].iloc[0]
        return pbkdf2_sha256.verify(password, stored_hash)
    return False

# -------------------- User Progress Handling --------------------
def load_user_progress():
    if os.path.exists('user_progress.csv'):
        df = pd.read_csv('user_progress.csv')
        if 'Redeemed_Rewards' in df.columns:
            df['Redeemed_Rewards'] = df['Redeemed_Rewards'].apply(lambda x: eval(x) if pd.notna(x) else [])
        if 'Quests_Completed' in df.columns:
            df['Quests_Completed'] = df['Quests_Completed'].apply(lambda x: eval(x) if pd.notna(x) else [])
        if 'Last_Check_In' in df.columns:
            df['Last_Check_In'] = pd.to_datetime(df['Last_Check_In'], errors='coerce')
        return df
    return pd.DataFrame(columns=['Username', 'XP', 'Coins', 'Redeemed_Rewards', 'Check_In_Streak', 'Last_Check_In', 'Quests_Completed', 'Quiz_Score'])

def save_user_progress(username, xp, coins, redeemed_rewards, check_in_streak, last_check_in, quests_completed, quiz_score):
    progress = load_user_progress()
    if username in progress['Username'].values:
        progress.loc[progress['Username'] == username, ['XP', 'Coins', 'Redeemed_Rewards', 'Check_In_Streak', 'Last_Check_In', 'Quests_Completed', 'Quiz_Score']] = [
            xp, coins, str(redeemed_rewards), check_in_streak, last_check_in, str(quests_completed), quiz_score
        ]
    else:
        new_progress = pd.DataFrame([[username, xp, coins, str(redeemed_rewards), check_in_streak, last_check_in, str(quests_completed), quiz_score]],
                                    columns=['Username', 'XP', 'Coins', 'Redeemed_Rewards', 'Check_In_Streak', 'Last_Check_In', 'Quests_Completed', 'Quiz_Score'])
        progress = pd.concat([progress, new_progress], ignore_index=True)
    progress.to_csv('user_progress.csv', index=False)

# -------------------- User Login --------------------
if 'username' not in st.session_state:
    st.title("💰 Finora - Student Budget Manager")
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if login_username and login_password:
                if verify_user(login_username, login_password):
                    st.session_state['username'] = login_username
                    st.session_state['goals'] = {}
                    # Load user progress
                    progress = load_user_progress()
                    if login_username in progress['Username'].values:
                        user_row = progress[progress['Username'] == login_username].iloc[0]
                        st.session_state['xp'] = user_row['XP']
                        st.session_state['coins'] = user_row['Coins']
                        st.session_state['redeemed_rewards'] = user_row['Redeemed_Rewards']
                        st.session_state['check_in_streak'] = user_row['Check_In_Streak']
                        st.session_state['last_check_in'] = user_row['Last_Check_In']
                        st.session_state['quests_completed'] = user_row['Quests_Completed']
                        st.session_state['quiz_score'] = user_row['Quiz_Score']
                    else:
                        st.session_state['xp'] = 0
                        st.session_state['coins'] = 0
                        st.session_state['redeemed_rewards'] = []
                        st.session_state['check_in_streak'] = 0
                        st.session_state['last_check_in'] = None
                        st.session_state['quests_completed'] = []
                        st.session_state['quiz_score'] = 0
                    st.success(f"Welcome, {login_username}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            else:
                st.warning("Please enter both username and password.")

    with tab2:
        st.subheader("Register")
        reg_username = st.text_input("Choose Username", key="reg_username")
        reg_password = st.text_input("Choose Password", type="password", key="reg_password")
        reg_confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")
        if st.button("Register"):
            if reg_username and reg_password and reg_confirm_password:
                users = load_users()
                if reg_username in users['Username'].values:
                    st.error("This username is already taken. Please choose a different username.")
                elif reg_password != reg_confirm_password:
                    st.error("Passwords do not match.")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    save_user(reg_username, reg_password)
                    st.success("Registration successful! Please log in.")
            else:
                st.warning("Please fill in all fields.")

    st.stop()
else:
    st.sidebar.success(f"👋 Welcome, {st.session_state['username']}!")
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# -------------------- Data Handling --------------------
if os.path.exists('user_data.csv'):
    st.session_state['data'] = pd.read_csv('user_data.csv', parse_dates=['Date'])
    if not all(col in st.session_state['data'].columns for col in ['Username', 'Type', 'Amount', 'Category', 'Date']):
        st.session_state['data']['Username'] = ''
        st.session_state['data'].to_csv('user_data.csv', index=False)
    if not pd.api.types.is_datetime64_any_dtype(st.session_state['data']['Date']):
        st.session_state['data']['Date'] = pd.to_datetime(st.session_state['data']['Date'], errors='coerce')
        if st.session_state['data']['Date'].isna().any():
            st.error("Some dates in the CSV are invalid. Please ensure all dates are in a valid format.")
            st.stop()
else:
    st.session_state['data'] = pd.DataFrame(columns=['Username', 'Type', 'Amount', 'Category', 'Date'])

# Filter data for the current user
data = st.session_state['data']
user_data = data[data['Username'] == st.session_state['username']].copy()

# -------------------- Sidebar Navigation --------------------
st.sidebar.markdown("## Main")
menu = st.sidebar.radio("Navigate", ["Dashboard", "Add Entry", "Set Goals", "Financial Education"],
                       format_func=lambda x: {
                           "Dashboard": "📊 Dashboard",
                           "Add Entry": "➕ Add Entry",
                           "Set Goals": "🎯 Set Goals",
                           "Financial Education": "📚 Financial Education"
                       }[x])
st.sidebar.markdown("---")
st.sidebar.markdown("## Data Management")
st.sidebar.markdown("📂 Upload/Download Data")
st.sidebar.markdown("---")
st.sidebar.markdown("## Learning")
st.sidebar.markdown("🧠 Set goals and learn financial tips!")

# -------------------- Set Goals --------------------
if menu == "Set Goals":
    st.subheader("🎯 Set Financial Goals")
    st.markdown("Set monthly budget or emergency fund goals to earn rewards!")
    
    # Monthly Budget Goals
    st.markdown("### 📅 Monthly Budget Goals")
    goal_type = st.selectbox("Goal Type", ["Savings", "Spending Limit"])
    goal_amount = st.number_input("Goal Amount (₹)", min_value=0.0, step=100.0, key="budget_goal")
    goal_month = st.date_input("For Month", value=datetime.today().replace(day=1)).strftime('%Y-%m')
    if st.button("Set Budget Goal"):
        if goal_amount > 0:
            st.session_state['goals'][goal_month] = {'type': goal_type, 'amount': goal_amount}
            st.success(f"{goal_type} goal of ₹{goal_amount} set for {goal_month}!")
        else:
            st.warning("Please enter a valid goal amount.")
    
    # Emergency Fund Goal
    st.markdown("### 🛡️ Emergency Fund Goal")
    emergency_goal = st.number_input("Emergency Fund Target (₹)", min_value=0.0, step=500.0, key="emergency_goal")
    if st.button("Set Emergency Fund Goal"):
        if emergency_goal > 0:
            st.session_state['emergency_fund_goal'] = emergency_goal
            st.success(f"Emergency fund goal set to ₹{emergency_goal}!")
        else:
            st.warning("Please enter a valid emergency fund goal.")

# -------------------- Add Entry --------------------
if menu == "Add Entry":
    st.subheader("➕ Add Income or Expense")
    entry_type = st.selectbox("Type", ["Income", "Expense"])
    amount = st.number_input("Amount", min_value=0.0, step=10.0)
    predefined_categories = ["Food", "Transport", "Entertainment", "Savings", "Education", "Rent", "Utilities", "Clothing", "Health", "Debt Repayment", "Other"]
    category = st.selectbox("Category", predefined_categories)
    if category == "Other":
        custom_category = st.text_input("Enter Custom Category")
        category = custom_category if custom_category else "Other"
    entry_date = st.date_input("Date", value=datetime.today().date())
    if st.button("Add Entry"):
        if category == "Other" and not custom_category:
            st.warning("Please enter a custom category name or select a predefined category.")
        elif amount <= 0:
            st.warning("Please enter a valid amount greater than 0.")
        else:
            new_entry = pd.DataFrame([[st.session_state['username'], entry_type, amount, category, pd.to_datetime(entry_date)]],
                                     columns=['Username', 'Type', 'Amount', 'Category', 'Date'])
            st.session_state['data'] = pd.concat([data, new_entry], ignore_index=True)
            st.session_state['data'].to_csv('user_data.csv', index=False)
            st.success("Entry added and saved successfully!")

# -------------------- Dashboard --------------------
elif menu == "Dashboard":
    st.subheader("📊 Dashboard")
    
    # Daily Check-In
    today = datetime.today().date()
    if st.session_state['last_check_in'] != today:
        if st.button("📅 Daily Check-In"):
            if st.session_state['last_check_in'] and (today - pd.Timestamp(st.session_state['last_check_in']).date()).days == 1:
                st.session_state['check_in_streak'] += 1
            else:
                st.session_state['check_in_streak'] = 1
            st.session_state['last_check_in'] = today
            st.session_state['xp'] += 5
            st.session_state['coins'] += 2
            save_user_progress(st.session_state['username'], st.session_state['xp'], st.session_state['coins'],
                              st.session_state['redeemed_rewards'], st.session_state['check_in_streak'],
                              st.session_state['last_check_in'], st.session_state['quests_completed'],
                              st.session_state['quiz_score'])
            st.success(f"Checked in! Current streak: {st.session_state['check_in_streak']} days (+5 XP, +2 Coins)")

    if user_data.empty:
        st.info("No data available. Add income and expenses to see dashboard.")
    else:
        user_data['Month'] = user_data['Date'].dt.to_period('M')
        current_month = pd.Timestamp.now().to_period('M')
        last_month = current_month - 1

        def get_summary(month):
            df = user_data[user_data['Month'] == month]
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
        summary = user_data.groupby(['Month', 'Type'])['Amount'].sum().unstack().fillna(0)
        st.line_chart(summary)

        st.markdown("### 🥧 Expense Breakdown")
        expense_data = user_data[(user_data['Type'] == 'Expense') & (user_data['Month'] == current_month)]
        if not expense_data.empty:
            pie_data = expense_data.groupby('Category')['Amount'].sum()
            if not pie_data.empty:
                fig, ax = plt.subplots()
                ax.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', colors=['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'])
                ax.axis('equal')
                st.pyplot(fig)
            else:
                st.info("No expense data available for the current month.")
        else:
            st.info("No expense data available for the current month.")

        st.markdown("### 📋 Full Data")
        st.dataframe(user_data[['Date', 'Type', 'Category', 'Amount']].sort_values(by='Date', ascending=False))

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
        st.markdown("### 🏅 Gamification Dashboard")
        total_income = user_data[user_data['Type'] == 'Income']['Amount'].sum()
        total_expense = user_data[user_data['Type'] == 'Expense']['Amount'].sum()
        total_saved = total_income - total_expense

        # Financial Quests
        st.markdown("#### 🗺️ Financial Quests")
        st.markdown("Complete quests to earn rewards and improve your financial skills!")
        quests = {
            "Expense Tracker": {"task": "Log 5 expenses in a week", "xp": 30, "coins": 10},
            "Savings Starter": {"task": "Save ₹2,000 in a month", "xp": 50, "coins": 20},
            "Budget Builder": {"task": "Log entries for 10 days", "xp": 40, "coins": 15},
            "Debt Crusher": {"task": "Pay off ₹1,000 in Debt Repayment", "xp": 40, "coins": 15},
            "Category Explorer": {"task": "Use 3 new categories in a month", "xp": 25, "coins": 10},
            "Consistency Star": {"task": "Log entries every day for 5 days in a week", "xp": 35, "coins": 12}
        }
        week_start = today - timedelta(days=today.weekday())
        recent_expenses = user_data[(user_data['Type'] == 'Expense') & (user_data['Date'].dt.date >= week_start)]
        unique_days = user_data['Date'].dt.date.nunique() if pd.api.types.is_datetime64_any_dtype(user_data['Date']) else 0
        debt_payments = user_data[(user_data['Type'] == 'Expense') & (user_data['Category'] == 'Debt Repayment')]['Amount'].sum()
        current_month_categories = user_data[user_data['Month'] == current_month]['Category'].nunique()
        week_days_logged = len(user_data[(user_data['Date'].dt.date >= week_start) & (user_data['Date'].dt.date <= today)]['Date'].dt.date.unique())
        
        for quest_name, quest_info in quests.items():
            if quest_name not in st.session_state['quests_completed']:
                if quest_name == "Expense Tracker" and len(recent_expenses) >= 5:
                    st.session_state['quests_completed'].append(quest_name)
                    st.session_state['xp'] += quest_info['xp']
                    st.session_state['coins'] += quest_info['coins']
                    save_user_progress(st.session_state['username'], st.session_state['xp'], st.session_state['coins'],
                                      st.session_state['redeemed_rewards'], st.session_state['check_in_streak'],
                                      st.session_state['last_check_in'], st.session_state['quests_completed'],
                                      st.session_state['quiz_score'])
                    st.success(f"🎉 Quest Completed: {quest_name}! Earned {quest_info['xp']} XP and {quest_info['coins']} coins!")
                elif quest_name == "Savings Starter" and balance >= 2000:
                    st.session_state['quests_completed'].append(quest_name)
                    st.session_state['xp'] += quest_info['xp']
                    st.session_state['coins'] += quest_info['coins']
                    save_user_progress(st.session_state['username'], st.session_state['xp'], st.session_state['coins'],
                                      st.session_state['redeemed_rewards'], st.session_state['check_in_streak'],
                                      st.session_state['last_check_in'], st.session_state['quests_completed'],
                                      st.session_state['quiz_score'])
                    st.success(f"🎉 Quest Completed: {quest_name}! Earned {quest_info['xp']} XP and {quest_info['coins']} coins!")
                elif quest_name == "Budget Builder" and unique_days >= 10:
                    st.session_state['quests_completed'].append(quest_name)
                    st.session_state['xp'] += quest_info['xp']
                    st.session_state['coins'] += quest_info['coins']
                    save_user_progress(st.session_state['username'], st.session_state['xp'], st.session_state['coins'],
                                      st.session_state['redeemed_rewards'], st.session_state['check_in_streak'],
                                      st.session_state['last_check_in'], st.session_state['quests_completed'],
                                      st.session_state['quiz_score'])
                    st.success(f"🎉 Quest Completed: {quest_name}! Earned {quest_info['xp']} XP and {quest_info['coins']} coins!")
                elif quest_name == "Debt Crusher" and debt_payments >= 1000:
                    st.session_state['quests_completed'].append(quest_name)
                    st.session_state['xp'] += quest_info['xp']
                    st.session_state['coins'] += quest_info['coins']
                    save_user_progress(st.session_state['username'], st.session_state['xp'], st.session_state['coins'],
                                      st.session_state['redeemed_rewards'], st.session_state['check_in_streak'],
                                      st.session_state['last_check_in'], st.session_state['quests_completed'],
                                      st.session_state['quiz_score'])
                    st.success(f"🎉 Quest Completed: {quest_name}! Earned {quest_info['xp']} XP and {quest_info['coins']} coins!")
                elif quest_name == "Category Explorer" and current_month_categories >= 3:
                    st.session_state['quests_completed'].append(quest_name)
                    st.session_state['xp'] += quest_info['xp']
                    st.session_state['coins'] += quest_info['coins']
                    save_user_progress(st.session_state['username'], st.session_state['xp'], st.session_state['coins'],
                                      st.session_state['redeemed_rewards'], st.session_state['check_in_streak'],
                                      st.session_state['last_check_in'], st.session_state['quests_completed'],
                                      st.session_state['quiz_score'])
                    st.success(f"🎉 Quest Completed: {quest_name}! Earned {quest_info['xp']} XP and {quest_info['coins']} coins!")
                elif quest_name == "Consistency Star" and week_days_logged >= 5:
                    st.session_state['quests_completed'].append(quest_name)
                    st.session_state['xp'] += quest_info['xp']
                    st.session_state['coins'] += quest_info['coins']
                    save_user_progress(st.session_state['username'], st.session_state['xp'], st.session_state['coins'],
                                      st.session_state['redeemed_rewards'], st.session_state['check_in_streak'],
                                      st.session_state['last_check_in'], st.session_state['quests_completed'],
                                      st.session_state['quiz_score'])
                    st.success(f"🎉 Quest Completed: {quest_name}! Earned {quest_info['xp']} XP and {quest_info['coins']} coins!")
                else:
                    st.info(f"Quest: {quest_name} - {quest_info['task']} (Reward: {quest_info['xp']} XP, {quest_info['coins']} coins)")

        # Achievements
        st.markdown("#### 🎖️ Achievements")
        st.markdown("Earn badges by managing your finances wisely!")
        achievements = []
        if total_saved >= 1000:
            achievements.append(("Budget Beginner", "Saved ₹1,000", "You've started building a savings habit!", datetime.now()))
            st.success("💸 **Budget Beginner** - Saved ₹1,000 (Meaning: You've started building a savings habit!)")
        if total_saved >= 5000:
            achievements.append(("Smart Saver", "Saved ₹5,000", "You're prioritizing financial security!", datetime.now()))
            st.success("🎯 **Smart Saver** - Saved ₹5,000 (Meaning: You're prioritizing financial security!)")
        if total_saved >= 10000:
            achievements.append(("Wealth Warrior", "Saved ₹10,000", "You're on the path to wealth creation!", datetime.now()))
            st.success("🏆 **Wealth Warrior** - Saved ₹10,000 (Meaning: You're on the path to wealth creation!)")
        if len(user_data) >= 10:
            achievements.append(("Consistency Champ", "10+ entries logged", "Consistent tracking is key to financial awareness!", datetime.now()))
            st.info("🗂️ **Consistency Champ** - 10+ entries logged (Meaning: Consistent tracking is key to financial awareness!)")
        if user_data['Category'].nunique() >= 5:
            achievements.append(("Diverse Tracker", "5+ unique categories", "You're understanding your spending patterns!", datetime.now()))
            st.info("🎨 **Diverse Tracker** - 5+ unique categories (Meaning: You're understanding your spending patterns!)")
        if user_data['Category'].nunique() >= 10:
            achievements.append(("Category Master", "10+ unique categories", "You're mastering comprehensive budgeting!", datetime.now()))
            st.info("🌈 **Category Master** - 10+ unique categories (Meaning: You're mastering comprehensive budgeting!)")

        # Logging Streak
        st.markdown("#### 🔥 Logging Streak")
        st.markdown("Log entries regularly to build a budgeting habit!")
        if pd.api.types.is_datetime64_any_dtype(user_data['Date']):
            user_data['DateOnly'] = user_data['Date'].dt.date
            unique_days = user_data['DateOnly'].nunique()
            st.info(f"📆 You've added entries on **{unique_days}** days!")
            if unique_days >= 3:
                achievements.append(("3-Day Streak", "Logged entries for 3 days", "Early consistency builds strong habits.", datetime.now()))
                st.success("🔥 **3-Day Streak** - Keep logging daily! (Meaning: Early consistency builds strong habits.)")
            if unique_days >= 7:
                achievements.append(("1-Week Streak", "Logged entries for 7 days", "You're forming a routine.", datetime.now()))
                st.success("🚀 **1-Week Streak** - One week strong! (Meaning: You're forming a routine.)")
            if unique_days >= 14:
                achievements.append(("2-Week Streak", "Logged entries for 14 days", "You're committed to financial tracking.", datetime.now()))
                st.success("🌟 **2-Week Streak** - Impressive dedication! (Meaning: You're committed to financial tracking.)")
            if unique_days >= 21:
                achievements.append(("3-Week Streak", "Logged entries for 21 days", "Long-term habits lead to success.", datetime.now()))
                st.success("⚡ **3-Week Streak** - Unstoppable! (Meaning: Long-term habits lead to success.)")
            if unique_days >= 30:
                achievements.append(("1-Month Consistency Hero", "Logged entries for 30 days", "You've built a solid foundation.", datetime.now()))
                st.success("🏅 **1-Month Consistency Hero** - A true budgeting pro! (Meaning: You've built a solid foundation.)")
            if unique_days >= 60:
                achievements.append(("2-Month Legend", "Logged entries for 60 days", "Your discipline is inspiring.", datetime.now()))
                st.success("👑 **2-Month Legend** - A budgeting legend! (Meaning: Your discipline is inspiring.)")
        else:
            st.warning("Date column is not in the correct format. Please ensure dates are valid.")

        # Savings Streak
        st.markdown("#### 💰 Savings Streak")
        st.markdown("Maintain positive balances monthly to grow your wealth!")
        if not user_data.empty:
            monthly_balances = user_data.groupby('Month').apply(lambda x: x[x['Type'] == 'Income']['Amount'].sum() - x[x['Type'] == 'Expense']['Amount'].sum())
            savings_streak = 0
            for month in sorted(monthly_balances.index, reverse=True):
                if monthly_balances[month] > 0:
                    savings_streak += 1
                else:
                    break
            st.info(f"📈 You've maintained a positive balance for **{savings_streak}** consecutive months!")
            if savings_streak >= 2:
                achievements.append(("Savings Sprout", "2+ months of positive balance", "Consistent saving builds wealth.", datetime.now()))
                st.success("🌱 **Savings Sprout** - 2+ months of positive balance! (Meaning: Consistent saving builds wealth.)")
            if savings_streak >= 4:
                achievements.append(("Savings Tree", "4+ months of positive balance", "Your savings are growing strong.", datetime.now()))
                st.success("🌳 **Savings Tree** - 4+ months of positive balance! (Meaning: Your savings are growing strong.)")
        else:
            st.info("Start adding entries to track your savings streak!")

        # Daily Check-In Streak
        st.markdown("#### 📅 Daily Check-In Streak")
        st.markdown("Check in daily to stay on top of your finances!")
        st.info(f"🔄 Current check-in streak: **{st.session_state['check_in_streak']}** days")
        if st.session_state['check_in_streak'] >= 3:
            achievements.append(("3-Day Check-In Streak", "Checked in for 3 days", "Regular monitoring keeps you in control.", datetime.now()))
            st.success("🌟 **3-Day Check-In Streak** - Great daily engagement! (Meaning: Regular monitoring keeps you in control.)")
        if st.session_state['check_in_streak'] >= 7:
            achievements.append(("7-Day Check-In Streak", "Checked in for 7 days", "You're mastering daily financial awareness.", datetime.now()))
            st.success("🚀 **7-Day Check-In Streak** - Amazing consistency! (Meaning: You're mastering daily financial awareness.)")

        # Emergency Fund Tracker
        st.markdown("#### 🛡️ Emergency Fund Tracker")
        st.markdown("Build a safety net for unexpected expenses!")
        emergency_savings = user_data[(user_data['Type'] == 'Income') & (user_data['Category'].str.lower() == 'savings')]['Amount'].sum()
        if st.session_state['emergency_fund_goal'] > 0:
            progress = min(emergency_savings / st.session_state['emergency_fund_goal'], 1.0)
            st.progress(progress)
            st.info(f"🛡️ Emergency Fund: ₹{emergency_savings:.2f} / ₹{st.session_state['emergency_fund_goal']:.2f} ({progress*100:.1f}%)")
            if progress >= 0.25:
                achievements.append(("Quarter Funded", "25% of emergency fund goal", "You're building a safety net.", datetime.now()))
                st.success("🏦 **Quarter Funded** - 25% of emergency fund goal! (Meaning: You're building a safety net.)")
            if progress >= 0.5:
                achievements.append(("Half Funded", "50% of emergency fund goal", "Your financial security is growing.", datetime.now()))
                st.success("🏧 **Half Funded** - 50% of emergency fund goal! (Meaning: Your financial security is growing.)")
            if progress >= 1.0:
                achievements.append(("Fully Funded", "Emergency fund goal achieved", "You're prepared for the unexpected.", datetime.now()))
                st.success("🎉 **Fully Funded** - Emergency fund goal achieved! (Meaning: You're prepared for the unexpected.)")
        else:
            st.info("Set an emergency fund goal in the 'Set Goals' tab!")

        # Monthly Goal Progress
        st.markdown("#### 🎯 Monthly Goal Progress")
        st.markdown("Track your savings or spending goals!")
        current_month_str = current_month.strftime('%Y-%m')
        if current_month_str in st.session_state['goals']:
            goal = st.session_state['goals'][current_month_str]
            if goal['type'] == 'Savings':
                progress = min(balance / goal['amount'], 1.0)
                st.progress(progress)
                st.info(f"💪 Savings Goal for {current_month_str}: ₹{balance:.2f} / ₹{goal['amount']} ({progress*100:.1f}%)")
                if balance >= goal['amount']:
                    achievements.append(("Goal Achiever", f"Met ₹{goal['amount']} savings goal", "You're hitting your financial targets!", datetime.now()))
                    st.success(f"🎉 **Goal Achiever** - Met ₹{goal['amount']} savings goal for {current_month_str}! (Meaning: You're hitting your financial targets!)")
                else:
                    st.info(f"Keep saving to reach your goal!")
            elif goal['type'] == 'Spending Limit':
                progress = max(1.0 - (expense_cur / goal['amount']), 0.0)
                st.progress(progress)
                st.info(f"💪 Spending Limit for {current_month_str}: ₹{expense_cur:.2f} / ₹{goal['amount']} ({progress*100:.1f}% under limit)")
                if expense_cur <= goal['amount']:
                    achievements.append(("Spending Master", f"Kept expenses under ₹{goal['amount']}", "You're controlling your spending!", datetime.now()))
                    st.success(f"🎉 **Spending Master** - Kept expenses under ₹{goal['amount']} for {current_month_str}! (Meaning: You're controlling your spending!)")
                else:
                    st.info(f"Try to cut back to meet your spending limit!")
        else:
            st.info("Set a monthly goal in the 'Set Goals' tab to track your progress!")

        # Badge Collection Gallery
        st.markdown("#### 🏅 Badge Collection Gallery")
        st.markdown("Showcase your earned badges!")
        if achievements or st.session_state['quests_completed']:
            st.markdown("**Your Badges**")
            for name, desc, meaning, date in achievements:
                st.markdown(f"- 🏆 **{name}** ({desc}) - *{meaning}* (Earned: {date.strftime('%Y-%m-%d')})")
            for quest in st.session_state['quests_completed']:
                st.markdown(f"- 🗺️ **{quest}** ({quests[quest]['task']}) - *Earned {quests[quest]['xp']} XP and {quests[quest]['coins']} coins!* (Earned: {datetime.now().strftime('%Y-%m-%d')})")
        else:
            st.info("Start earning badges by completing quests and achieving financial milestones!")

        # Peer Comparison Rank
        st.markdown("#### 🏅 Peer Comparison Rank")
        st.markdown("See how you stack up against other budgeters!")
        total_users = len(data['Username'].unique()) if not data.empty else 1
        user_xp = st.session_state['xp']
        peer_xps = [user_xp] + [random.randint(50, 500) for _ in range(total_users - 1)]
        rank = sum(1 for peer_xp in peer_xps if peer_xp > user_xp) + 1
        percentile = (1 - rank / total_users) * 100
        if percentile >= 90:
            achievements.append(("Top 10% Budgeter", f"Rank {rank}/{total_users}", "You're among the best savers!", datetime.now()))
            st.success(f"🌟 **Top 10% Budgeter** - Rank {rank}/{total_users}! (Meaning: You're among the best savers!)")
        elif percentile >= 75:
            achievements.append(("Rising Star", f"Rank {rank}/{total_users}", "Your budgeting skills are shining!", datetime.now()))
            st.success(f"🚀 **Rising Star** - Rank {rank}/{total_users}! (Meaning: Your budgeting skills are shining!)")
        else:
            st.info(f"📈 Rank {rank}/{total_users} ({percentile:.1f}% percentile). Keep budgeting to climb the ranks!")

        # XP and Levels
        def calculate_xp(data):
            income_entries = data[data['Type'] == 'Income'].shape[0]
            expense_entries = data[data['Type'] == 'Expense'].shape[0]
            xp = (income_entries * 5) + (expense_entries * 3)
            if current_month_str in st.session_state['goals']:
                goal = st.session_state['goals'][current_month_str]
                if goal['type'] == 'Savings' and balance >= goal['amount']:
                    xp += 50
                elif goal['type'] == 'Spending Limit' and expense_cur <= goal['amount']:
                    xp += 50
            if unique_days >= 7:
                xp += 20
            if unique_days >= 30:
                xp += 50
            if savings_streak >= 2:
                xp += 30
            if st.session_state['check_in_streak'] >= 3:
                xp += 10
            if st.session_state['check_in_streak'] >= 7:
                xp += 20
            if emergency_savings >= st.session_state['emergency_fund_goal'] * 0.5:
                xp += 30
            if emergency_savings >= st.session_state['emergency_fund_goal']:
                xp += 50
            for quest_name in st.session_state['quests_completed']:
                xp += quests[quest_name]['xp']
            xp += st.session_state['quiz_score'] * 5
            return xp

        st.session_state['xp'] = calculate_xp(user_data)
        level = st.session_state['xp'] // 100 + 1
        next_level_xp = (level * 100) - st.session_state['xp']
        st.markdown(f"#### 🎮 Level: {level}")
        st.progress((st.session_state['xp'] % 100) / 100)
        st.caption(f"⭐ {st.session_state['xp']} XP - {next_level_xp} XP to next level!")

        # Coins and Redemption
        st.session_state['coins'] = st.session_state['xp'] // 10 + sum(quests[quest]['coins'] for quest in st.session_state['quests_completed'])
        st.sidebar.markdown(f"💰 Coins Earned: **{st.session_state['coins']}**")
        st.markdown("#### 🏪 Coin Redemption")
        st.markdown("Redeem coins for virtual rewards to enhance your financial knowledge!")
        available_rewards = {
            "Advanced Financial Tips": {"cost": 100, "description": "Unlock expert budgeting strategies."},
            "Investment Guide": {"cost": 150, "description": "Learn about mutual funds and stocks."},
            "Savings Master Badge": {"cost": 200, "description": "Earn a prestigious badge for your profile."}
        }
        selected_reward = st.selectbox("Choose a Reward", [""] + list(available_rewards.keys()))
        if st.button("Redeem Reward") and selected_reward:
            if selected_reward in available_rewards:
                cost = available_rewards[selected_reward]["cost"]
                if st.session_state['coins'] >= cost and selected_reward not in st.session_state['redeemed_rewards']:
                    st.session_state['redeemed_rewards'].append(selected_reward)
                    st.session_state['coins'] -= cost
                    save_user_progress(st.session_state['username'], st.session_state['xp'], st.session_state['coins'],
                                      st.session_state['redeemed_rewards'], st.session_state['check_in_streak'],
                                      st.session_state['last_check_in'], st.session_state['quests_completed'],
                                      st.session_state['quiz_score'])
                    st.success(f"🎁 Redeemed: {selected_reward}! {available_rewards[selected_reward]['description']}")
                elif selected_reward in st.session_state['redeemed_rewards']:
                    st.error("You've already redeemed this reward.")
                else:
                    st.warning(f"You need {cost - st.session_state['coins']} more coins to redeem {selected_reward}.")
            else:
                st.error("Please select a valid reward.")

        # Display Redeemed Rewards
        if st.session_state['redeemed_rewards']:
            st.markdown("#### 🏆 Your Redeemed Rewards")
            for reward in st.session_state['redeemed_rewards']:
                st.info(f"🎉 {reward}: {available_rewards[reward]['description']}")

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
    if "Advanced Financial Tips" in st.session_state['redeemed_rewards']:
        st.markdown("### 🎁 Advanced Financial Tips (Unlocked)")
        st.markdown("""
        - 📊 Use the 50/30/20 rule: 50% needs, 30% wants, 20% savings/debt repayment.
        - 🔄 Review your budget monthly to adjust for new goals.
        - 🛠️ Build an emergency fund covering 3-6 months of expenses.
        """)

    st.markdown("### 🗞️ Latest Financial News")
    with st.expander("Click to View"):
        st.markdown("- Sensex climbs 300 points; Nifty above 23,500 ahead of Fed decision")
        st.markdown("- Gold prices drop as dollar strengthens on Fed signals")
        st.markdown("- Mutual Fund SIPs hit record ₹18,000 crore in June 2025")
    if "Investment Guide" in st.session_state['redeemed_rewards']:
        st.markdown("### 📈 Investment Guide (Unlocked)")
        st.markdown("""
        - 📚 **Mutual Funds**: Diversify investments with SIPs for steady growth.
        - 📈 **Stocks**: Research companies with strong fundamentals for long-term gains.
        - 🏦 **Fixed Deposits**: Safe option for guaranteed returns, ideal for students.
        """)

    # Financial Quiz Challenge
    st.markdown("### 📝 Financial Quiz Challenge")
    st.markdown("Test your financial knowledge and earn XP!")
    quiz_questions = [
        {"question": "What is the 50/30/20 budgeting rule?", "options": ["50% needs, 30% wants, 20% savings", "50% savings, 30% needs, 20% wants", "50% wants, 30% needs, 20% savings"], "correct": 0},
        {"question": "What is a mutual fund?", "options": ["A single stock", "A diversified investment pool", "A fixed deposit"], "correct": 1},
        {"question": "Why is an emergency fund important?", "options": ["To buy luxury items", "To cover unexpected expenses", "To invest in stocks"], "correct": 1}
    ]
    if st.button("Start Quiz"):
        st.session_state['quiz_score'] = 0
        for i, q in enumerate(quiz_questions):
            st.markdown(f"**Question {i+1}: {q['question']}**")
            answer = st.radio("Select an answer:", q['options'], key=f"quiz_{i}")
            if st.button("Submit Answer", key=f"submit_{i}"):
                if q['options'].index(answer) == q['correct']:
                    st.session_state['quiz_score'] += 1
                    st.success("Correct! +1 point")
                else:
                    st.error("Incorrect. Try again next time!")
        st.session_state['xp'] += st.session_state['quiz_score'] * 5
        save_user_progress(st.session_state['username'], st.session_state['xp'], st.session_state['coins'],
                          st.session_state['redeemed_rewards'], st.session_state['check_in_streak'],
                          st.session_state['last_check_in'], st.session_state['quests_completed'],
                          st.session_state['quiz_score'])
        st.info(f"Quiz Score: {st.session_state['quiz_score']}/3 (Earned {st.session_state['quiz_score'] * 5} XP)")
        peer_scores = [st.session_state['quiz_score']] + [random.randint(0, 3) for _ in range(9)]
        quiz_rank = sum(1 for score in peer_scores if score > st.session_state['quiz_score']) + 1
        st.metric("Quiz Leaderboard Rank", f"{quiz_rank}/10")

# -------------------- Upload & Download --------------------
st.sidebar.file_uploader("Upload CSV", type="csv", key="file_uploader")
if st.session_state.get('file_uploader'):
    uploaded_file = st.session_state['file_uploader']
    uploaded_data = pd.read_csv(uploaded_file, parse_dates=['Date'])
    if all(col in uploaded_data.columns for col in ['Username', 'Type', 'Amount', 'Category', 'Date']):
        if pd.api.types.is_datetime64_any_dtype(uploaded_data['Date']):
            uploaded_data = uploaded_data[uploaded_data['Username'] == st.session_state['username']]
            if not uploaded_data.empty:
                non_user_data = data[data['Username'] != st.session_state['username']]
                st.session_state['data'] = pd.concat([non_user_data, uploaded_data], ignore_index=True)
                st.session_state['data'].to_csv('user_data.csv', index=False)
                st.success("Data uploaded successfully for your account!")
            else:
                st.error("No data in the uploaded CSV matches your username.")
        else:
            st.error("Date column in uploaded CSV is not in a valid datetime format.")
    else:
        st.error("Uploaded CSV must contain columns: Username, Type, Amount, Category, Date")

user_csv = user_data.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("Download My Data", user_csv, f"{st.session_state['username']}_budget_data.csv", "text/csv")

