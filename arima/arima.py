import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_squared_error, mean_absolute_error
import requests

# Data Collection and Preparation
def fetch_bitcoin_data():
    url = 'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart'
    params = {'vs_currency': 'usd', 'days': 'max', 'interval': 'daily'}
    response = requests.get(url, params=params)
    data = response.json()
    prices = data['prices']
    df = pd.DataFrame(prices, columns=['Date', 'Close_Price'])
    df['Date'] = pd.to_datetime(df['Date'], unit='ms')
    df.set_index('Date', inplace=True)
    df['Close_Price'].fillna(method='ffill', inplace=True)
    return df

data = fetch_bitcoin_data()

# Exploratory Data Analysis (EDA)
plt.figure(figsize=(10, 6))
plt.plot(data['Close_Price'])
plt.title('Bitcoin Daily Closing Prices')
plt.xlabel('Date')
plt.ylabel('Close Price')
plt.show()

# Rolling mean and standard deviation
rolling_mean = data['Close_Price'].rolling(window=30).mean()
rolling_std = data['Close_Price'].rolling(window=30).std()

plt.figure(figsize=(10, 6))
plt.plot(data['Close_Price'], label='Original')
plt.plot(rolling_mean, label='Rolling Mean')
plt.plot(rolling_std, label='Rolling Std')
plt.legend()
plt.show()

# Autocorrelation and partial autocorrelation plots
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

plot_acf(data['Close_Price'])
plot_pacf(data['Close_Price'])
plt.show()

# Decomposition
from statsmodels.tsa.seasonal import seasonal_decompose

decomposition = seasonal_decompose(data['Close_Price'], model='multiplicative', period=365)
decomposition.plot()
plt.show()

# Augmented Dickey-Fuller test
result = adfuller(data['Close_Price'])
print('ADF Statistic:', result[0])
print('p-value:', result[1])

# Model Selection and Parameter Tuning
model = auto_arima(data['Close_Price'], start_p=0, start_q=0,
                   test='adf', max_p=5, max_q=5, m=1,
                   d=None, seasonal=False, start_P=0,
                   D=0, trace=True, error_action='ignore',
                   suppress_warnings=True, stepwise=True)

print(model.summary())

# Model Training
train_size = int(len(data) * 0.8)
train_data, test_data = data[:train_size], data[train_size:]

model = ARIMA(train_data['Close_Price'], order=model.order)
results = model.fit()
print(results.summary())

# Forecasting
forecast = results.forecast(steps=len(test_data))
forecast_index = test_data.index

plt.figure(figsize=(10, 6))
plt.plot(train_data['Close_Price'], label='Train')
plt.plot(test_data['Close_Price'], label='Test')
plt.plot(forecast_index, forecast, label='Forecast')
plt.legend()
plt.show()

# Model Validation and Refinement
mse = mean_squared_error(test_data['Close_Price'], forecast)
mae = mean_absolute_error(test_data['Close_Price'], forecast)
rmse = np.sqrt(mse)

print(f'MSE: {mse}, MAE: {mae}, RMSE: {rmse}')

# Iterate and Improve
# Implement a rolling forecast (example for next 7 days)
rolling_forecast = results.get_forecast(steps=7)
rolling_forecast_index = pd.date_range(start=data.index[-1], periods=8, closed='right')

plt.figure(figsize=(10, 6))
plt.plot(data['Close_Price'], label='Historical')
plt.plot(rolling_forecast_index, rolling_forecast.predicted_mean, label='Rolling Forecast')
plt.legend()
plt.show()