import streamlit as st
import yfinance as yf
import pandas as pd

# --- THEME CONFIGURATION ---
st.set_page_config(page_title="Aladdin | Market Home", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #050a14; color: #e0e1dd; }
    [data-testid="stMetric"] { background: #1b263b; border: 1px solid #415a77; border-radius: 10px; padding: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ BHARAT-ALADDIN | MARKET HOME")

# --- LIVE MARKET PULSE ---
col1, col2, col3 = st.columns(3)

# Fetching Nifty & VIX
nifty = yf.download("^NSEI", period="2d", progress=False)
vix = yf.download("^INDIAVIX", period="2d", progress=False)

with col1:
    n_price = nifty['Close'].iloc[-1]
    n_change = ((n_price - nifty['Close'].iloc[-2]) / nifty['Close'].iloc[-2]) * 100
    st.metric("NIFTY 50", f"{n_price:.2f}", f"{n_change:.2f}%")

with col2:
    v_val = vix['Close'].iloc[-1]
    st.metric("INDIA VIX", f"{v_val:.2f}", "Volatile" if v_val > 20 else "Stable", delta_color="inverse")

with col3:
    # Simulated FII/DII - In a production app, use a dedicated scraper
    st.metric("FII NET (PROVISIONAL)", "-1,440 Cr", "Selling")

st.divider()
st.subheader("📊 Sector Strength (Top Indices)")
# Add more index tracking here (BankNifty, IT, Auto)
