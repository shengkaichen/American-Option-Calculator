import Calculator
import GUI
import QuantLib as ql
import numpy as np

# option data
option_type = "put"
stock_price = 15.50
strike_price = 20
volatility = 0.5815  # the historical vols or implied vols
risk_free_rate = 0.0152
dividend_rate = 0.0135
exercise_date = ql.Date(19, 11, 2021)  # day-month-year
today_date = ql.Date(6, 10, 2021)
days_to_hold = 5
stock_float = 0.05  # percentage

# results
model = Calculator.Option(option_type, stock_price, strike_price, volatility, risk_free_rate,
                          dividend_rate, exercise_date, today_date, days_to_hold,
                          stock_float)

print("\n")
print("Future Stock Price : ", stock_price * (1 + stock_float))
print("Option Price : ", np.around(model.option_price(), decimals=2))
print("\n")

# print(model.option_table().to_string())

GUI.ui(model.option_table())
