import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Bharat-Aladdin | Apex", layout="wide")

class BharatAladdin:
    def fetch_data(self, ticker, is_index=False):
        # India VIX ticker can be tricky, we try the most common one
        symbol = ticker if is_index else f"{ticker.strip()}.NS"
        df = yf.download(symbol, period="1y", interval="1d", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df

    def get_market_regime(self):
        # India VIX is the barometer for F&O Regime
        vix_df = self.fetch_data("^INDIAVIX", is_index=True)
        if vix_df.empty or len(vix_df) < 1:
            return "Unknown", 0.0
        current_vix = float(vix_df['Close'].iloc[-1])
        
        if current_vix < 15:
            return "🛡️ CALM (Option Selling Preferred)", current_vix
        elif current_vix < 25:
            return "⚖️ NORMAL (Balanced Strategies)", current_vix
        else:
            return "🔥 FEAR (Hedged Buying Only)", current_vix

    def calculate_logic(self, df):
        if df.empty or len(df) < 50:
            return None
        # Inside calculate_logic(self, df):
vol_avg = df['Volume'].rolling(window=20).mean().iloc[-1]
curr_vol = df['Volume'].iloc[-1]
volume_surge = curr_vol > (vol_avg * 1.5) # 50% spike

if volume_surge and price > ema:
    score += 30 # High conviction
    reasons.append("🔥 SMART MONEY: Significant volume surge detected.")
elif volume_surge and price < ema:
    reasons.append("⚠️ DISTRIBUTION: Heavy volume on a downward trend.")
    
        # 1. Trend Factor
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
        price = float(df['Close'].iloc[-1])
        ema = float(df['EMA50'].iloc[-1])
        
        # 2. Smart Money Factor (Volume Surge)
        vol_avg = df['Volume'].rolling(20).mean().iloc[-1]
        curr_vol = df['Volume'].iloc[-1]
        volume_surge = curr_vol > (vol_avg * 1.5)

        score = 0
        reasons = []
        
        if price > ema:
            score += 50
            reasons.append("Trend: Bullish (Above 50 EMA)")
        else:
            reasons.append("Trend: Bearish (Below 50 EMA)")
            
        if volume_surge:
            score += 30
            reasons.append("Smart Money: High Volume Surge")
        
        dist_to_ema = ((price - ema) / ema) * 100
        if dist_to_ema > 10:
            score -= 20
            reasons.append("Risk: Overextended")

        return {"score": int(score), "reasons": reasons, "price": price, "dist": dist_to_ema}

# --- DASHBOARD UI ---
engine = BharatAladdin()
st.title("🛡️ Bharat-Aladdin: Apex Intelligence")

# Section 1: F&O Regime
regime, vix_val = engine.get_market_regime()
st.info(f"**Current F&O Regime:** {regime} | **India VIX:** {vix_val:.2f}")

watchlist = st.text_input("Enter Tickers", "RELIANCE, SBIN, TCS, INFOTEE, HDFCBANK, ICICIBANK")
tickers = [t.strip().upper() for t in watchlist.split(",")]

if st.button("🔥 Run Apex Analysis"):
    master_data = []
    for ticker in tickers:
        try:
            data = engine.fetch_data(ticker)
            result = engine.calculate_logic(data)
            if result:
                master_data.append({
                    "Symbol": ticker,
                    "Score": result['score'],
                    "Price": round(result['price'], 2),
                    "Gap %": round(result['dist'], 2),
                    "Analysis": " | ".join(result['reasons'])
                })
        except:
            continue

    if master_data:
        df_display = pd.DataFrame(master_data).sort_values(by="Score", ascending=False)
        st.subheader("🏆 Conviction Rankings")
        
        # FIXED: Using st.dataframe with column configuration for better styling in new Streamlit
        st.dataframe(
            df_display,
            column_config={
                "Score": st.column_config.ProgressColumn(
                    "Aladdin Score",
                    help="Conviction score (0-100)",
                    format="%d",
                    min_value=0,
                    max_value=100,
                ),
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.error("No valid data found.")
