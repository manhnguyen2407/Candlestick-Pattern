import pandas as pd
import yfinance as yf

from prophet import Prophet
from typing import Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta

start_date = datetime.now() - relativedelta(years=3)
end_date = datetime.now()
df_raw = yf.download('HPG.VN', start=start_date, end=end_date)
df_reset = df_raw.reset_index()
df = df_reset[['Date','Adj Close']].rename(columns={'Date': 'ds', 'Adj Close': 'y'})

m = Prophet()
m.fit(df)

future = m.make_future_dataframe(periods=365)
future.tail()

forecast = m.predict(future)
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

fig2 = m.plot_components(forecast)



