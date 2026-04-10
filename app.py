import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- 1. PREMIUM TERMINAL STYLING ---
st.set_page_config(page_title="Bharat-Aladdin | Apex Terminal", layout="wide")

st.markdown("""
    <style>
    /* Premium Midnight Blue Theme */
    .stApp {
        background: radial-gradient(circle at top left, #050a14 0%, #0d1b2a 100%);
        color: #e0e1dd;
    }
    
    /* Metrics & Cards Styling */
    [data-testid="stMetric"] {
        background: rgba(27, 38, 59, 0.6);
        border: 1px solid #415a77;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(4px);
    }
    
    /* Custom News Ticker */
    .news-card {
        background: #1b263b;
        border-left: 4px solid #778da9;
        padding: 10px;
        margin-bottom: 5px;
        border-radius: 4px;
        font-size: 0.85rem;
    }

    h1, h2, h3 { color: #8ecae6 !important; }
    </style>
    """, unsafe_allow_html=True)

class AladdinApex:
    def fetch_data(self, ticker, is_index=False):
        symbol = ticker if is_index else f"{ticker.strip()}.NS"
        df = yf.download(symbol, period="1y", interval="1d", progress=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df

    def get_fii_dii_context(self):
        # Simulated context based on recent trends for display
        # In a real app, this would scrape NSE / MoneyControl
        return {"FII": "-1,240 Cr (Selling)", "DII": "+2,100 Cr (Buying)", "Trend": "Institutional Support at Lows"}

    def get_news(self, tickers):
        # Pulls basic news metadata for the first ticker in the list
        main_stock = yf.Ticker(f"{tickers[0]}.NS")
        return main_stock.news[:5]

# --- 2. TERMINAL DASHBOARD ---
engine = AladdinApex()
st.title("🛡️ BHARAT-ALADDIN | APEX TERMINAL")

# TOP ROW: F&O REGIME & INSTITUTIONAL FLOW
col_vix, col_fii, col_dii = st.columns(3)
vix_df = engine.fetch_data("^INDIAVIX", is_index=True)
vix_val = float(vix_df['Close'].iloc[-1]) if not vix_df.empty else 0.0
fii_dii = engine.get_fii_dii_context()

with col_vix: st.metric("INDIA VIX", f"{vix_val:.2f}", "Normal Range" if vix_val < 22 else "High Vol")
with col_fii: st.metric("FII DATA (Daily)", fii_dii["FII"])
with col_dii: st.metric("DII DATA (Daily)", fii_dii["DII"])

st.divider()

# MIDDLE ROW: SCANNER & NEWS
col_scan, col_news = st.columns([2, 1])

with col_scan:
    watchlist = st.text_input("📡 TERMINAL SCANNER", "RELIANCE, SBIN, TCS, HDFCBANK, ICICIBANK")
    tickers = [t.strip().upper() for t in watchlist.split(",")]
    
    if st.button("⚡ EXECUTE SYSTEM SCAN"):
        master_data = []
        for ticker in tickers:
            try:
                data = engine.fetch_data(ticker)
                # Quick Logic Calculation
                price = float(data['Close'].iloc[-1])
                ema50 = data['Close'].ewm(span=50, adjust=False).mean().iloc[-1]
                score = 60 if price > ema50 else 20
                
                master_data.append({
                    "Symbol": ticker,
                    "Score": score,
                    "Price": round(price, 2),
                    "Trend": "Bullish" if price > ema50 else "Bearish"
                })
            except: continue
        
        st.dataframe(pd.DataFrame(master_data), use_container_width=True, hide_index=True)

with col_news:
    st.subheader("📰 Live Market Feed")
    news_items = engine.get_news(tickers)
    for item in news_items:
        st.markdown(f"""
            <div class="news-card">
                <b>{item['publisher']}</b>: {item['title'][:60]}...<br>
                <small>Sentiment: Analysis Pending</small>
            </div>
        """, unsafe_allow_html=True)
