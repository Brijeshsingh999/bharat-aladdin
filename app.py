import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Aladdin India", layout="wide")

class BharatAladdin:
    def fetch_data(self, ticker):
        df = yf.download(f"{ticker}.NS", period="1y", interval="1d", progress=False)
        return df

    def calculate_logic(self, df):
        # Standard Technical Indicators without extra libraries
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()
        
        # Simple RSI calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        curr = df.iloc[-1]
        score = 0
        details = []
        
        # Trend
        if curr['Close'] > curr['EMA50']:
            score += 40
            details.append("✅ Above 50 EMA")
        
        # Risk Check
        dist_to_ema = ((curr['Close'] - curr['EMA50']) / curr['EMA50']) * 100
        if dist_to_ema > 8:
            score -= 20
            details.append("⚠️ Overextended from EMA")

        return score, details, curr, dist_to_ema

# --- UI ---
st.title("🛡️ Bharat-Aladdin")
watchlist = st.text_input("Tickers", "RELIANCE, SBIN, TCS")
tickers = [t.strip().upper() for t in watchlist.split(",")]

engine = BharatAladdin()

for ticker in tickers:
    try:
        data = engine.fetch_data(ticker)
        score, reasons, last_row, dist = engine.calculate_logic(data)
        
        color = "#238636" if score > 20 else "#da3633"
        st.markdown(f"""<div style="border-left: 10px solid {color}; padding:15px; background:#161b22; margin-bottom:10px;">
            <h3>{ticker}: ₹{last_row['Close']:.2f} (Score: {score})</h3>
        </div>""", unsafe_allow_headers=True)
        st.write(", ".join(reasons))
    except:
        st.error(f"Error on {ticker}")
