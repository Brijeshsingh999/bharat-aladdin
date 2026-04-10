import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime

# --- SYSTEM SETTINGS ---
st.set_page_config(page_title="Aladdin India", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for a clean, "Aladdin" Bloomberg-style dark theme
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    .decision-card { padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b; background-color: #1c2128; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_headers=True)

class BharatAladdin:
    def __init__(self):
        self.risk_free_rate = 0.07  # India 10Y Bond Yield approx

    def fetch_data(self, ticker):
        df = yf.download(f"{ticker}.NS", period="2y", interval="1d", progress=False)
        return df

    def calculate_logic(self, df):
        # 1. Trend (Explainable)
        df['EMA50'] = ta.ema(df['Close'], length=50)
        df['EMA200'] = ta.ema(df['Close'], length=200)
        
        # 2. Momentum
        df['RSI'] = ta.rsi(df['Close'], length=14)
        
        # 3. Smart Money (Volume Price Trend)
        df['VPT'] = ta.vpt(df['Close'], df['Volume'])
        
        curr = df.iloc[-1]
        prev = df.iloc[-2]

        # Scoring Logic
        score = 0
        details = []
        
        # Trend Component (40 pts)
        if curr['Close'] > curr['EMA50']:
            score += 20
            details.append("✅ Price above 50 EMA (Short-term Strength)")
        if curr['EMA50'] > curr['EMA200']:
            score += 20
            details.append("✅ Golden Crossover Context (Long-term Bullish)")

        # Smart Money / Volume (30 pts)
        if curr['Volume'] > df['Volume'].tail(20).mean():
            score += 30
            details.append("🔥 High Volume: Institutional activity suspected")
        
        # Risk Component (Negative Weights)
        risk_score = 0
        dist_to_ema = ((curr['Close'] - curr['EMA50']) / curr['EMA50']) * 100
        if dist_to_ema > 8:
            risk_score += 20
            details.append("⚠️ Overextended: Price > 8% from 50 EMA. Risk of mean reversion.")
        
        if curr['RSI'] > 75:
            risk_score += 15
            details.append("⚠️ RSI Overbought: Potential exhaustion.")

        final_score = score - risk_score
        return final_score, details, curr, dist_to_ema

# --- APP INTERFACE ---
engine = BharatAladdin()

st.title("🛡️ Bharat-Aladdin")
st.caption("Quantitative Decision Support for Indian Cash Equity")

# 1. Market Overview Section
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    nifty = yf.download("^NSEI", period="5d", progress=False)
    change = ((nifty['Close'].iloc[-1] - nifty['Close'].iloc[-2]) / nifty['Close'].iloc[-2]) * 100
    st.metric("NIFTY 50", f"{nifty['Close'].iloc[-1]:.2f}", f"{change:.2f}%")

# 2. Input Section
watchlist = st.text_input("Enter NSE Tickers (e.g. RELIANCE, HDFCBANK, TATASTEEL)", "RELIANCE, SBIN, TCS")
tickers = [t.strip().upper() for t in watchlist.split(",")]

st.divider()

# 3. Decision Engine Output
for ticker in tickers:
    try:
        data = engine.fetch_data(ticker)
        score, reasons, last_row, dist = engine.calculate_logic(data)
        
        # Assign Decision Color
        if score > 40:
            color = "#238636" # Green
            decision = "BUY / ACCUMULATE"
        elif score > 10:
            color = "#8e7b11" # Yellow
            decision = "HOLD / WATCH"
        else:
            color = "#da3633" # Red
            decision = "NO-TRADE / EXIT"

        # UI Card
        st.markdown(f"""
            <div style="padding:20px; border-radius:10px; border-left: 10px solid {color}; background-color: #161b22; margin-bottom:15px;">
                <h2 style="margin:0;">{ticker} <span style="font-size:15px; color:#8b949e;">| Price: ₹{last_row['Close']:.2f}</span></h2>
                <h3 style="color:{color}; margin:5px 0;">Decision: {decision} (Score: {score})</h3>
            </div>
        """, unsafe_allow_headers=True)
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("#### Logic Breakdown")
            for r in reasons:
                st.write(r)
        with c2:
            st.markdown("#### Risk Analysis")
            st.write(f"**Distance to 50 EMA:** {dist:.2f}%")
            st.write(f"**RSI (14):** {last_row['RSI']:.2f}")
            if dist > 5:
                st.error("Position Sizing: Small (High Risk due to Price Extension)")
            else:
                st.success("Position Sizing: Standard (Healthy Entry Zone)")
        st.divider()
    except Exception as e:
        st.error(f"Error analyzing {ticker}: {e}")

st.markdown("---")
st.caption("Data provided via yfinance. Aladdin logic proprietary to user personal use. Not financial advice.")
