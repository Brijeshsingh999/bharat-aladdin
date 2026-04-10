import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Bharat-Aladdin", layout="wide")

class BharatAladdin:
    def fetch_data(self, ticker):
        # We add .NS for National Stock Exchange
        symbol = f"{ticker.strip()}.NS"
        # Using period='1mo' for a faster initial test
        df = yf.download(symbol, period="1y", interval="1d", progress=False, auto_adjust=True)
        return df

    def calculate_logic(self, df):
        if df.empty:
            return None, None, None, None
            
        # Standard Technical Indicators
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
        
        # Simple RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        curr = df.iloc[-1]
        score = 0
        details = []
        
        if curr['Close'] > curr['EMA50']:
            score += 40
            details.append("✅ Above 50 EMA")
        else:
            details.append("❌ Below 50 EMA")
            
        dist_to_ema = ((curr['Close'] - curr['EMA50']) / curr['EMA50']) * 100

        return score, details, curr, dist_to_ema

# --- UI ---
st.title("🛡️ Bharat-Aladdin")
watchlist = st.text_input("Tickers (Use simple names like RELIANCE, SBIN)", "RELIANCE, SBIN, TCS")
tickers = [t.strip().upper() for t in watchlist.split(",")]

engine = BharatAladdin()

if st.button("Run Analysis"):
    for ticker in tickers:
        try:
            data = engine.fetch_data(ticker)
            if data.empty:
                st.error(f"Could not find data for {ticker}. Check if the symbol is correct.")
                continue
                
            score, reasons, last_row, dist = engine.calculate_logic(data)
            
            color = "#238636" if score >= 40 else "#da3633"
            st.markdown(f"""
                <div style="border-left: 10px solid {color}; padding:15px; background:#161b22; margin-bottom:10px; border-radius: 5px;">
                    <h3 style="margin:0;">{ticker}: ₹{float(last_row['Close']):.2f}</h3>
                    <p style="margin:5px 0;">Score: {score} | Distance to EMA: {dist:.2f}%</p>
                </div>
            """, unsafe_allow_headers=True)
            
            for r in reasons:
                st.write(r)
        except Exception as e:
            st.error(f"Technical Error on {ticker}: {e}")
