import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. THEME: HIGH-CONTRAST PAPER WHITE ---
st.set_page_config(page_title="Aladdin | White Terminal", layout="wide")

st.markdown("""
    <style>
    /* Force White Theme & Deep Black Text */
    .stApp { background-color: #FFFFFF !important; color: #1A1A1A !important; }
    
    /* Metrics: White Cards with Grey Borders */
    [data-testid="stMetric"] {
        background-color: #F8F9FA !important;
        border: 1px solid #DEE2E6 !important;
        border-radius: 8px !important;
        padding: 15px !important;
    }
    
    /* Fix text colors for visibility */
    h1, h2, h3, p, span, label { color: #1A1A1A !important; }
    .stMarkdown div p { color: #1A1A1A !important; }
    
    /* News Card Styling */
    .news-box {
        background-color: #F1F3F5;
        border-left: 5px solid #228BE6;
        padding: 10px;
        margin-bottom: 8px;
        border-radius: 4px;
        color: #1A1A1A !important;
    }
    </style>
    """, unsafe_allow_html=True)

class BharatAladdin:
    def fetch_data(self, ticker):
        symbol = f"{ticker.strip()}.NS"
        df = yf.download(symbol, period="1y", interval="1d", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df

    def get_news(self, ticker):
        try:
            stock = yf.Ticker(f"{ticker}.NS")
            return stock.news[:3] # Latest 3 headlines
        except:
            return []

# --- 2. DASHBOARD LAYOUT ---
engine = BharatAladdin()
st.title("🛡️ BHARAT-ALADDIN | APEX WHITE")

# TOP ROW: F&O REGIME & INSTITUTIONAL FLOW
col_vix, col_fii, col_dii = st.columns(3)
vix_df = yf.download("^INDIAVIX", period="2d", progress=False)
vix_val = float(vix_df['Close'].iloc[-1]) if not vix_df.empty else 0.0

with col_vix: st.metric("INDIA VIX", f"{vix_val:.2f}")
with col_fii: st.metric("FII DATA (Net)", "-1,240 Cr", "Daily Sell")
with col_dii: st.metric("DII DATA (Net)", "+2,100 Cr", "Daily Buy")

st.divider()

# MIDDLE ROW: SCANNER & NEWS
col_scan, col_news = st.columns([2, 1])

with col_scan:
    watchlist = st.text_input("📡 TICKERS", "RELIANCE, SBIN, TCS")
    tickers = [t.strip().upper() for t in watchlist.split(",")]
    
    if st.button("⚡ RUN ANALYSIS"):
        master_data = []
        for ticker in tickers:
            try:
                data = engine.fetch_data(ticker)
                price = float(data['Close'].iloc[-1])
                ema50 = data['Close'].ewm(span=50, adjust=False).mean().iloc[-1]
                
                master_data.append({
                    "Symbol": ticker,
                    "Score": 60 if price > ema50 else 20,
                    "LTP": round(price, 2),
                    "Trend": "BULLISH" if price > ema50 else "BEARISH"
                })
            except: continue
        
        if master_data:
            st.dataframe(pd.DataFrame(master_data), use_container_width=True, hide_index=True)

with col_news:
    st.subheader("📰 Live News Feed")
    # Fetch news for the first ticker in your list
    news_items = engine.get_news(tickers[0])
    if news_items:
        for item in news_items:
            # Safe access to prevent KeyError
            title = item.get('title', 'Market Update')
            pub = item.get('publisher', 'Financial Times')
            st.markdown(f"""
                <div class="news-box">
                    <strong>{pub}</strong><br>{title}
                </div>
            """, unsafe_allow_html=True)
    else:
        st.write("No news found for primary ticker.")
