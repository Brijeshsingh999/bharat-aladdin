import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Bharat-Aladdin", layout="wide")

class BharatAladdin:
    def fetch_data(self, ticker):
        symbol = f"{ticker.strip()}.NS"
        df = yf.download(symbol, period="1y", interval="1d", progress=False)
        
        # Flatten Multi-Index columns if they exist
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df

    def calculate_logic(self, df):
        if df.empty or len(df) < 50:
            return None, None, None, None
            
        # Technicals
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        curr = df.iloc[-1]
        score = 0
        details = []
        
        price = float(curr['Close'])
        ema = float(curr['EMA50'])
        
        if price > ema:
            score += 40
            details.append("✅ Price is above 50-day EMA (Bullish Trend)")
        else:
            details.append("❌ Price is below 50-day EMA (Bearish Trend)")
            
        dist_to_ema = ((price - ema) / ema) * 100

        return score, details, price, dist_to_ema

# --- UI ---
st.title("🛡️ Bharat-Aladdin")
watchlist = st.text_input("Tickers (Example: RELIANCE, SBIN, TCS)", "RELIANCE")
tickers = [t.strip().upper() for t in watchlist.split(",")]

engine = BharatAladdin()

if st.button("Run Analysis"):
    for ticker in tickers:
        try:
            data = engine.fetch_data(ticker)
            score, reasons, price, dist = engine.calculate_logic(data)
            
            if score is None:
                st.warning(f"Not enough data for {ticker}")
                continue

            color = "#238636" if score >= 40 else "#da3633"
            
            # FIXED: Changed unsafe_allow_headers to unsafe_allow_html
            st.markdown(f"""
                <div style="border-left: 10px solid {color}; padding:15px; background:#161b22; margin-bottom:10px; border-radius: 5px;">
                    <h3 style="margin:0; color:white;">{ticker}: ₹{price:.2f}</h3>
                    <p style="margin:5px 0; font-weight:bold; color:{color};">Score: {score} | Distance to EMA: {dist:.2f}%</p>
                </div>
            """, unsafe_allow_html=True)
            
            for r in reasons:
                st.write(r)
        except Exception as e:
            st.error(f"Error on {ticker}: {str(e)}")
