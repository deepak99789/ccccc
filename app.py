import streamlit as st
import pandas as pd
from data_fetcher import get_forex_data
from strategy import find_zones
import plotly.graph_objects as go

st.set_page_config(page_title="Supply Demand Screener", layout="centered")
st.markdown("<h1 style='text-align: center;'>📊 Supply Demand Screener</h1>", unsafe_allow_html=True)

with st.form("screener_form"):
    script_type = st.selectbox("Select Script Type", ["Currency", "Commodity", "Crypto"])
    base_candle_num = st.slider("Number of Base Candles", 1, 6, 1)
    timeframe = st.selectbox("Select Time Interval", ["1m","5m","15m","30m","60m","1h","2h","4h","6h","8h","10h","12h","1d","1w"], index=3)
    zone_status = st.selectbox("Zone Status", ["All", "Fresh", "Target", "Stoploss"], index=0)
    zone_type = st.selectbox("Zone Type", ["All", "Supply", "Demand"], index=0)
    scan_btn = st.form_submit_button("🔍 SCAN")

if scan_btn:
    pair_map = {"Currency":"EURUSD=X","Commodity":"GC=F","Crypto":"BTC-USD"}
    symbol = pair_map[script_type]
    df = get_forex_data(symbol, interval=timeframe, limit=200)
    zones = find_zones(df)

    if zone_type != "All":
        zones = zones[zones['Zone']==zone_type]

    latest_price = df["close"].iloc[-1]
    def zone_status_filter(row):
        if row["Zone"]=="Demand":
            if latest_price < row["Entry"]:
                return "Fresh"
            elif latest_price >= row["Target(1:3)"]:
                return "Target"
            elif latest_price <= row["StopLoss"]:
                return "Stoploss"
        else:
            if latest_price > row["Entry"]:
                return "Fresh"
            elif latest_price <= row["Target(1:3)"]:
                return "Target"
            elif latest_price >= row["StopLoss"]:
                return "Stoploss"
        return "Fresh"

    zones["Current_Status"] = zones.apply(zone_status_filter, axis=1)
    if zone_status != "All":
        zones = zones[zones["Current_Status"]==zone_status]

    st.write("### 📝 Scan Results")
    st.dataframe(zones)

    if not zones.empty:
        latest_zone = zones.iloc[-1]
        st.success(f"Latest Zone: {latest_zone['Pattern']} ({latest_zone['Zone']}) at {latest_zone['Base_Time']}")

        fig = go.Figure(data=[go.Candlestick(
            x=df["timestamp"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], name="Candles"
        )])
        color = "green" if latest_zone["Zone"]=="Demand" else "red"
        fig.add_hline(y=latest_zone["Entry"], line=dict(color=color, dash="dash"), annotation_text=f"Entry {latest_zone['Pattern']}", annotation_position="top right")
        fig.add_hline(y=latest_zone["StopLoss"], line=dict(color="orange", dash="dot"), annotation_text="SL", annotation_position="bottom right")
        fig.add_hline(y=latest_zone["Target(1:3)"], line=dict(color="blue", dash="dot"), annotation_text="Target 1:3", annotation_position="top right")
        fig.update_layout(title=f"{symbol} - {timeframe} (Latest Zone: {latest_zone['Pattern']})", xaxis_rangeslider_visible=False, height=600)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No zones found for selected filters.")
