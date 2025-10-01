import yfinance as yf
import pandas as pd

def get_forex_data(symbol, interval='1h', limit=200):
    interval_map = {
        "1m":"1m","5m":"5m","15m":"15m","30m":"30m","60m":"60m","1h":"60m",
        "2h":"120m","4h":"240m","6h":"360m","8h":"480m","10h":"600m","12h":"720m",
        "1d":"1d","1w":"1wk"
    }
    yf_interval = interval_map.get(interval, "1h")
    data = yf.download(symbol, period="60d", interval=yf_interval)
    data = data.tail(limit)
    data.reset_index(inplace=True)
    data.rename(columns={"Open":"open","High":"high","Low":"low","Close":"close","Volume":"volume","Date":"timestamp"}, inplace=True)
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    return data
