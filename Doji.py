import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go

start_date = (datetime.now() - relativedelta(years=3)).strftime("%Y-%m-%d")
end_date = datetime.now().strftime("%Y-%m-%d")

def BodyAVG(df: pd.DataFrame, l: int) -> float | None:
    if l - 14 < 0:
        return None
    elif l - 14 == 0:
        SMA = df.Body.iloc[0:14].mean()
        return df.Body[l] * 2 / 15 + SMA * 13 / 15
    else:
        return df.BodyAvg[l - 1] * 13 / 15 + df.Body[l] * 2 / 15

def get_data(Symbol: str, StartDate: str, EndDate: str) -> Optional[pd.DataFrame]:
    df = yf.download(Symbol + ".VN", start=StartDate, end=EndDate)
    df["BodyHi"] = df[["Open", "Close"]].max(axis=1)
    df["BodyLo"] = df[["Open", "Close"]].min(axis=1)
    df["Body"] = df["BodyHi"] - df["BodyLo"]
    df.reset_index(inplace=True)
    df["BodyAvg"] = np.nan
    for i in range(len(df)):
        df.at[i, "BodyAvg"] = BodyAVG(df=df, l=i)
    df["SmallBody"] = np.where(df["BodyAvg"].isnull(), None, (df["Body"] < df["BodyAvg"]).astype(int))
    df["LongBody"] = np.where(df["BodyAvg"].isnull(), None, (df["Body"] > df["BodyAvg"]).astype(int))
    df["UpShadow"] = df["High"] - df["BodyHi"]
    df["DnShadow"] = df["BodyLo"] - df["Low"]
    df["Range"] = df["High"] - df["Low"]
    df["DojiBody"] = ((df["Range"] > 0) & (df["Body"] <= df["Range"] * 0.05 / 100)).astype(int)
    df["ShadowEquals"] = (((df["UpShadow"] == df["DnShadow"]) | (abs(df["UpShadow"] - df["DnShadow"]) / df["DnShadow"] * 100 < 100)) & (abs(df["DnShadow"] - df["UpShadow"]) / df["UpShadow"] * 100 < 100)).astype(int)
    df["Doji"] = ((df["DojiBody"] == 1) & (df["ShadowEquals"] == 1)).astype(int)
    return df[["Date", "Open", "High", "Low", "Close", "BodyHi", "BodyLo", "Body", "BodyAvg", "SmallBody", "LongBody", "UpShadow", "DnShadow", "Range", "DojiBody", "ShadowEquals", "Doji"]]

def pointpos(df: pd.DataFrame) -> float:
    if df["Doji"] == 1:
        return df["High"] + 1e-3
    else:
        return np.nan

def plot_doji(Symbol: str, StartDate: str = start_date, EndDate: str = end_date) -> None:
    df = get_data(Symbol=Symbol, StartDate=StartDate, EndDate=EndDate)
    df["pointpos"] = df.apply(lambda row: pointpos(row), axis=1)
    date_range = [d.strftime("%Y-%m-%d") for d in pd.date_range(start=StartDate, end=EndDate).tolist()]
    date_df = [d.strftime("%Y-%m-%d") for d in df["Date"]]
    date_breaks = [d for d in date_range if not d in date_df]

    fig = go.Figure(data=[go.Candlestick(
        x=df["Date"],
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name=Symbol
    )])

    fig.add_scatter(x=df["Date"], y=df["pointpos"], mode="markers",
                    marker=dict(size=5, color="MediumPurple"),
                    name="Doji")
    
    fig.update_layout(xaxis_rangeslider_visible=False,
                xaxis_type="date",
                xaxis_tickformat="%d/%m/%Y",
                xaxis_rangebreaks=[
                    dict(values=date_breaks)
                ])
    
    fig.show()

plot_doji(Symbol="HPG")
