import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

from typing import Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta

start_date = (datetime.now() - relativedelta(years=3)).strftime("%Y-%m-%d")
end_date = datetime.now().strftime("%Y-%m-%d")

def get_data(Symbol: str, StartDate: str, EndDate: str) -> pd.DataFrame:
    df = yf.download(Symbol + ".VN", start=StartDate, end=EndDate)
    df["EP"] = df["Low"]
    df["Acc"] = 0.02
    df["PSAR-EP*Acc"] = (df["High"] - df["EP"]) * df["Acc"]
    df["InitialPSAR"] = None
    df["PSAR"] = df["High"]
    df["Trend"] = "Falling"
    df.reset_index(inplace=True)

    for index in range(1, len(df)):
        # Tính InitialPSAR
        if df.loc[index - 1, "Trend"] == "Falling":
            if index == 1:
                df.loc[index, "InitialPSAR"] = max(df.loc[index - 1, "PSAR"] - df.loc[index - 1, "PSAR-EP*Acc"], df.loc[index - 1, "High"])
            else:
                df.loc[index, "InitialPSAR"] = max(df.loc[index - 1, "PSAR"] - df.loc[index - 1, "PSAR-EP*Acc"], df.loc[index - 1, "High"], df.loc[index - 2, "High"])
        else:
            if index == 1:
                df.loc[index, "InitialPSAR"] = min(df.loc[index - 1, "PSAR"] - df.loc[index - 1, "PSAR-EP*Acc"], df.loc[index - 1, "Low"])
            else:
                df.loc[index, "InitialPSAR"] = min(df.loc[index - 1, "PSAR"] - df.loc[index - 1, "PSAR-EP*Acc"], df.loc[index - 1, "Low"], df.loc[index - 2, "Low"])
        
        # Tính PSAR
        if (df.loc[index - 1, "Trend"] == "Falling" and df.loc[index, "High"] < df.loc[index, "InitialPSAR"]) or (df.loc[index - 1, "Trend"] == "Rising" and df.loc[index, "High"] > df.loc[index, "InitialPSAR"]):
            df.loc[index, "PSAR"] = df.loc[index, "InitialPSAR"]
        else:
            df.loc[index, "PSAR"] = df.loc[index - 1, "EP"]
        
        # Tính Trend
        if df.loc[index, "PSAR"] > df.loc[index, "Close"]:
            df.loc[index, "Trend"] = "Falling"
        else:
            df.loc[index, "Trend"] = "Rising"
        
        # Tính EP
        if df.loc[index, "Trend"] == "Falling":
            df.loc[index, "EP"] = min(df.loc[index - 1, "EP"], df.loc[index, "Low"])
        else:
            df.loc[index, "EP"] = max(df.loc[index - 1, "EP"], df.loc[index, "High"])
        
        # Tính Acc
        if df.loc[index, "Trend"] == df.loc[index - 1, "Trend"] and df.loc[index, "EP"] != df.loc[index - 1, "EP"] and df.loc[index - 1, "Acc"] < 0.2:
            df.loc[index, "Acc"] = df.loc[index - 1, "Acc"] + 0.02
        elif df.loc[index, "Trend"] == df.loc[index - 1, "Trend"] and df.loc[index, "EP"] == df.loc[index - 1, "EP"]:
            df.loc[index, "Acc"] = df.loc[index - 1, "Acc"]
        elif df.loc[index, "Trend"] != df.loc[index - 1, "Trend"]:
            df.loc[index, "Acc"] = 0.02
        else:
            df.loc[index, "Acc"] = 0.2

        # Tính PSAR-EP*Acc
        df.loc[index, "PSAR-EP*Acc"] = (df.loc[index, "PSAR"] - df.loc[index, "EP"]) * df.loc[index, "Acc"]

    return df[["Date", "Open", "High", "Low", "Close", "Volume", "EP", "Acc", "PSAR-EP*Acc", "InitialPSAR", "PSAR", "Trend"]]

def plot_SAR(Symbol: str, StartDate: str = start_date, EndDate: str = end_date) -> None:
    df = get_data(Symbol="HPG", StartDate=StartDate, EndDate=EndDate)

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

    color_map = {'Rising': 'blue', 'Falling': 'red'}

    for Trending in df["Trend"].unique():
        subset = df[df["Trend"] == Trending]
        fig.add_scatter(
            x=subset["Date"],
            y=subset["PSAR"],
            mode="markers",
            name=Trending,
            marker=dict(size=5, color=color_map[Trending])
        )
    
    fig.update_layout(xaxis_rangeslider_visible=False,
                xaxis_type="date",
                xaxis_tickformat="%d/%m/%Y",
                xaxis_rangebreaks=[
                    dict(values=date_breaks)
                ])
    
    fig.show()

plot_SAR(Symbol="HPG", StartDate="2023-03-17", EndDate="2024-05-30")
