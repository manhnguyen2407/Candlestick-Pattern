import pandas as pd
import matplotlib.pyplot as plt

# Giả sử bạn có dữ liệu về giá hàng tháng
data = {
    'Month': ['2023-01', '2023-02', '2023-03', '2023-04', '2023-05', 
              '2023-06', '2023-07', '2023-08', '2023-09', '2023-10'],
    'Price': [100, 110, 105, 115, 120, 125, 130, 128, 135, 140]
}
df = pd.DataFrame(data)
df['Month'] = pd.to_datetime(df['Month'])
df.set_index('Month', inplace=True)

# Hiển thị dữ liệu
print(df)

# Vẽ biểu đồ
"""df['Price'].plot(title='Dữ liệu giá hàng tháng', figsize=(10, 5))
plt.xlabel('Tháng')
plt.ylabel('Giá')
plt.show()"""

from statsmodels.tsa.stattools import adfuller

result = adfuller(df['Price'])
print(f"ADF Statistic: {result[0]}")
print(f"p-value: {result[1]}")

if result[1] > 0.05:
    print("Chuỗi không dừng, cần lấy sai phân.")
else:
    print("Chuỗi đã dừng.")
# Lấy sai phân

df['Price_diff'] = df['Price'].diff().dropna()

# ACF và PACF
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

plot_acf(df['Price'], lags=5)
plt.title('ACF')
plt.show()

plot_pacf(df['Price'], lags=5)
plt.title('PACF')
plt.show()

from statsmodels.tsa.statespace.sarimax import SARIMAX

# Khởi tạo mô hình SARIMA với các tham số (1, 1, 1)x(1, 1, 1, 12)
model = SARIMAX(df['Price'], 
                order=(1, 1, 1), 
                seasonal_order=(1, 1, 1, 12))

# Huấn luyện mô hình
results = model.fit()

# Tóm tắt mô hình
print(results.summary())

# Dự báo 6 bước tiếp theo
forecast = results.forecast(steps=6)
print("Dự báo:", forecast)

# Vẽ biểu đồ
plt.figure(figsize=(10, 5))
plt.plot(df['Price'], label='Thực tế')
plt.plot(forecast, label='Dự báo', linestyle='--')
plt.legend()
plt.title('Dự báo với SARIMA')
plt.xlabel('Thời gian')
plt.ylabel('Giá')
plt.show()