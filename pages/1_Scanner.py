import streamlit as st
import yfinance as yf
import pandas as pd

st.title("🔍 Advanced Scanner")

watchlist = st.text_area("Enter Tickers (one per line)", "RELIANCE\nSBIN\nTCS\nINFOTEE")
tickers = [t.strip().upper() for t in watchlist.split("\n")]

if st.button("Run Multi-Factor Scan"):
    results = []
    for t in tickers:
        df = yf.download(f"{t}.NS", period="60d", progress=False)
        if len(df) < 20: continue
        
        # Logic: Price > 20 SMA AND Volume > 1.5x Avg
        df['SMA20'] = df['Close'].rolling(20).mean()
        avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
        
        curr_price = df['Close'].iloc[-1]
        curr_vol = df['Volume'].iloc[-1]
        
        is_smart_money = curr_vol > (avg_vol * 1.5)
        is_bullish = curr_price > df['SMA20'].iloc[-1]
        
        results.append({
            "Symbol": t,
            "Price": round(curr_price, 2),
            "Signal": "🚀 SMART MONEY" if (is_smart_money and is_bullish) else "Neutral",
            "Volume Surge": round(curr_vol/avg_vol, 2)
        })
    
    st.table(pd.DataFrame(results).sort_values(by="Volume Surge", ascending=False))
