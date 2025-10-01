import pandas as pd

def candle_type(row):
    body = abs(row["close"] - row["open"])
    rng = row["high"] - row["low"]
    if rng == 0:
        return "Base"
    body_pct = body / rng
    if row["close"] > row["open"] and body_pct > 0.5:
        return "Rally"
    elif row["close"] < row["open"] and body_pct > 0.5:
        return "Drop"
    else:
        return "Base"

def find_zones(df: pd.DataFrame):
    df = df.copy()
    df["type"] = df.apply(candle_type, axis=1)
    zones = []
    for i in range(2, len(df)):
        leg_in = df["type"].iloc[i-2]
        base   = df["type"].iloc[i-1]
        leg_out= df["type"].iloc[i]
        timestamp = df["timestamp"].iloc[i-1]
        low = df["low"].iloc[i-1]
        high = df["high"].iloc[i-1]
        pattern = None
        zone_type = None
        entry = sl = target = None
        if leg_in == "Rally" and base == "Base" and leg_out == "Rally":
            pattern = "RBR"
            zone_type = "Demand"
        elif leg_in == "Rally" and base == "Base" and leg_out == "Drop":
            pattern = "RBD"
            zone_type = "Supply"
        elif leg_in == "Drop" and base == "Base" and leg_out == "Drop":
            pattern = "DBD"
            zone_type = "Supply"
        elif leg_in == "Drop" and base == "Base" and leg_out == "Rally":
            pattern = "DBR"
            zone_type = "Demand"
        if pattern:
            if zone_type == "Demand":
                entry = high
                sl = low
                target = entry + (entry - sl)*3
            if zone_type == "Supply":
                entry = low
                sl = high
                target = entry - (sl - entry)*3
            zones.append({
                "Pattern": pattern,
                "Zone": zone_type,
                "Base_Low": low,
                "Base_High": high,
                "Base_Time": timestamp,
                "Entry": entry,
                "StopLoss": sl,
                "Target(1:3)": target
            })
    return pd.DataFrame(zones)
