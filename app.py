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

try:
    # Fetching Nifty & VIX (2 days to calculate change)
    nifty = yf.download("^NSEI", period="2d", progress=False)
    vix = yf.download("^INDIAVIX", period="2d", progress=False)

    # Flatten columns if Multi-Index (yfinance 0.2.40+ behavior)
    if isinstance(nifty.columns, pd.MultiIndex):
        nifty.columns = nifty.columns.get_level_values(0)
    if isinstance(vix.columns, pd.MultiIndex):
        vix.columns = vix.columns.get_level_values(0)

    with col1:
        # We use .item() or float() to ensure a single number is passed
        n_price = float(nifty['Close'].iloc[-1])
        n_prev = float(nifty['Close'].iloc[-2])
        n_change = ((n_price - n_prev) / n_prev) * 100
        st.metric("NIFTY 50", f"{n_price:.2f}", f"{n_change:.2f}%")

    with col2:
        v_val = float(vix['Close'].iloc[-1])
        st.metric("INDIA VIX", f"{v_val:.2f}", "Volatile" if v_val > 20 else "Stable", delta_color="inverse")

    with col3:
        # Provisional placeholder for FII Data
        st.metric("FII NET (PROVISIONAL)", "-1,440 Cr", "Daily Change")

except Exception as e:
    st.error(f"Waiting for market data refresh... (Error: {e})")

st.divider()
st.subheader("📊 Sector Strength")
st.info("Navigate to the **Scanner** in the sidebar to run deep-dive analysis on specific stocks.")
