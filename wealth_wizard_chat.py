import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
import stripe
from io import BytesIO

# Stripe setup (replace with your keys in Render environment variables)
stripe.api_key = st.secrets.get("STRIPE_API_KEY", "sk_test_...")  # Use test key initially

# DB setup for persistence (SQLite for simplicity; upgrade to PostgreSQL later)
conn = sqlite3.connect('wealth_wizard.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (user_id TEXT PRIMARY KEY, pay REAL, age INT, risk TEXT, chat_history TEXT)''')
conn.commit()

# Helper: Get/Set user data
def get_user_data(user_id):
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    return row if row else None

def save_user_data(user_id, pay, age, risk, history):
    c.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?, ?)", 
              (user_id, pay, age, risk, ','.join(history)))
    conn.commit()

# Subscription check (simplified; use webhooks in production)
def is_subscribed(user_id):
    try:
        customers = stripe.Customer.search(query=f'email:"{user_id}"')  # Assuming user_id is email
        if customers.data:
            subs = stripe.Subscription.list(customer=customers.data[0].id)
            return any(sub.status == 'active' for sub in subs.data)
    except:
        pass
    return False  # Default to false

# Main app
st.set_page_config(page_title="WealthWizard 🪄", layout="wide")

# Hide Streamlit branding
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none !important;}
    </style>
    """, unsafe_allow_html=True)

# User login (simple; expand with auth lib)
user_id = st.sidebar.text_input("Enter your email (as user ID):")
if not user_id:
    st.warning("Enter your email to start!")
    st.stop()

subscribed = is_subscribed(user_id)
if not subscribed:
    st.sidebar.warning("Subscribe for full chatbot access!")
    if st.sidebar.button("Subscribe Now ($6.99/mo)"):
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price': 'price_...your_price_id', 'quantity': 1}],  # Create in Stripe dashboard
            mode='subscription',
            success_url=st.secrets.get("DOMAIN", "http://localhost") + "/?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=st.secrets.get("DOMAIN", "http://localhost"),
            customer_email=user_id
        )
        st.markdown(f"[Pay with Stripe]({session.url})", unsafe_allow_html=True)
    # Free tier: Basic projection only
    st.title("WealthWizard Free Tier ✨")
    pay = st.number_input("Weekly Pay ($)", value=1000.0)
    invest_pct = st.slider("Invest %", 0, 50, 20) / 100
    return_pct = st.slider("Expected Return %", 4, 15, 8) / 100
    weekly_invest = pay * invest_pct
    st.write(f"Weekly Investment: ${weekly_invest:.2f}")
    # Add basic projections here if needed (from earlier code)
else:
    # Premium: Chatbot mode
    st.title(f"Welcome back, {user_id}! Your Personal Wealth Coach 🧙‍♂️")

    # Load user data
    data = get_user_data(user_id)
    if data:
        pay, age, risk, history_str = data[1], data[2], data[3], data[4]
        chat_history = history_str.split(',') if history_str else []
    else:
        pay, age, risk, chat_history = 1000.0, 30, "Balanced", []

    # Inputs (persistent)
    col1, col2 = st.columns(2)
    with col1:
    pay = st.number_input("Weekly Pay ($)", value=pay)
    age = st.number_input("Age", value=age, min_value=18)
