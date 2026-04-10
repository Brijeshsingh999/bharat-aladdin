import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- 1. TERMINAL STYLING (The "Un-Boring" Layer) ---
st.set_page_config(page_title="Aladdin Apex", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for a professional Bloomberg-style Dark Theme
st.markdown("""
    <style>
    /* Main Background & Glassmorphism */
    .stApp { background: linear-gradient(135deg, #0e1117 0%, #1c2128 100%); }
    
    /* Custom Info Box Styling */
    .stAlert { background-color: rgba(30, 34, 42, 0.8) !important; border: 1px solid #30363d !important; border-radius: 10px !important; }
    
    /* Header Styling */
    h1 { font-family: 'Inter', sans-serif; font-weight: 800; letter-spacing: -1px; color: #e6edf3; }
    
    /* Grid Card Simulation */
    [data-testid="stMetric"] { background: rgba(22, 27, 34, 0.7); border: 1px solid #30363d; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

class BharatAladdin:
    def fetch_data(self, ticker, is_index=False):
        symbol = ticker if is_index else f"{ticker.strip()}.NS"
        df = yf.download(symbol, period="1y", interval="1d", progress=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df

    def get_strategy_logic(self, vix):
        """Aladdin F&O Strategy Recommender"""
        if vix < 15: return "🛡️ CALM", "Bull Put Spreads / Naked Buying"
        elif vix < 22: return "⚖️ NORMAL", "Iron Condors / Credit Spreads"
        else: return "🔥 VOLATILE", "Iron Fly / Hedged Butterfly"

    def calculate_logic(self, df):
        if df.empty or len(df) < 50: return None
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
        price, ema = float(df['Close'].iloc[-1]), float(df['EMA50'].iloc[-1])
        vol_avg, curr_vol = df['Volume'].rolling(20).mean().iloc[-1], df['Volume'].iloc[-1]
        
        score, reasons = 0, []
        if price > ema:
            score += 50
            reasons.append("Bullish Trend")
        if curr_vol > (vol_avg * 1.5):
            score += 30
            reasons.append("Smart Money Surge")
        
        dist = ((price - ema) / ema) * 100
        if dist > 10: score -= 20
        
        return {"score": int(score), "reasons": " | ".join(reasons), "price": price, "dist": dist}

# --- 2. TERMINAL UI ---
engine = BharatAladdin()
st.title("🛡️ BHARAT-ALADDIN | APEX TERMINAL")

# Market Intelligence Header
vix_df = engine.fetch_data("^INDIAVIX", is_index=True)
vix_val = float(vix_df['Close'].iloc[-1]) if not vix_df.empty else 0.0
regime, recommended_strat = engine.get_strategy_logic(vix_val)

col1, col2, col3 = st.columns(3)
with col1: st.metric("INDIA VIX", f"{vix_val:.2f}")
with col2: st.metric("REGIME", regime)
with col3: st.metric("RECO STRATEGY", recommended_strat.split("/")[0])

st.info(f"💡 **F&O Insight:** Based on current volatility, favor: **{recommended_strat}**")

# Input Section
watchlist = st.text_input("📡 TERMINAL SCANNER (Tickers separated by comma)", "RELIANCE, SBIN, TCS, HDFCBANK, ICICIBANK")
tickers = [t.strip().upper() for t in watchlist.split(",")]

if st.button("⚡ EXECUTE SYSTEM SCAN"):
    master_data = []
    for ticker in tickers:
        try:
            data = engine.fetch_data(ticker)
            res = engine.calculate_logic(data)
            if res:
                master_data.append({
                    "Symbol": ticker,
                    "Score": res['score'],
                    "Price": round(res['price'], 2),
                    "Gap %": round(res['dist'], 2),
                    "Analysis": res['reasons'],
                    "Strategy Path": recommended_strat if res['score'] > 40 else "N/A"
                })
        except: continue

    if master_data:
        df = pd.DataFrame(master_data).sort_values(by="Score", ascending=False)
        st.subheader("🏆 CONVICTION LEADERBOARD")
        
        # Professional Grid Output
        st.dataframe(
            df,
            column_config={
                "Score": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=100, format="%d"),
                "Gap %": st.column_config.NumberColumn("Risk Dist.", format="%.2f%%"),
                "Price": st.column_config.NumberColumn("LTP", format="₹%.2f"),
                "Strategy Path": "F&O Roadmap"
            },
            hide_index=True,
            use_container_width=True
        )
