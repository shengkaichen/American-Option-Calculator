import QuantLib as ql
import numpy as np
import pandas as pd


class Option:
    def __init__(self, option_types: str, stock_prices, strike_prices, v, risk_free_rates,
                 dividend_rates, exercise_dates, today_dates, days_to_holds, stock_floats):
        self.option_type = option_types
        self.stock_prices = stock_prices
        self.strike_prices = strike_prices
        self.v = v
        self.risk_free_rates = risk_free_rates
        self.dividend_rates = dividend_rates
        self.exercise_dates = exercise_dates
        self.today_dates = today_dates
        self.days_to_holds = days_to_holds
        self.stock_floats = stock_floats

    # calculate option price
    def option_price(self):
        if self.option_type == "call":
            self.option_type = ql.Option.Call
        elif self.option_type == "put":
            self.option_type = ql.Option.Put
        day_count = ql.Actual365Fixed()
        calendar = ql.UnitedStates()
        calculation_date = self.today_dates + ql.Period(self.days_to_holds, ql.Days)
        ql.Settings.instance().evaluationDate = calculation_date

        target_stock_price = self.stock_prices * (1 + self.stock_floats)

        payoff = ql.PlainVanillaPayoff(self.option_type, self.strike_prices)
        exercise = ql.AmericanExercise(calculation_date, self.exercise_dates)
        option = ql.VanillaOption(payoff, exercise)

        spot_handle = ql.QuoteHandle(
            ql.SimpleQuote(target_stock_price))
        flat_ts = ql.YieldTermStructureHandle(
            ql.FlatForward(calculation_date, self.risk_free_rates, day_count))
        dividend_yield = ql.YieldTermStructureHandle(
            ql.FlatForward(calculation_date, self.dividend_rates, day_count))
        flat_vol_ts = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(calculation_date, calendar, self.v, day_count))
        process = ql.BlackScholesMertonProcess(spot_handle, dividend_yield, flat_ts, flat_vol_ts)

        results = []
        average = []

        # Barone-Adesi-Whaley Model
        option.setPricingEngine(ql.BaroneAdesiWhaleyApproximationEngine(process))
        results.append(("Barone-Adesi-Whaley", option.NPV()))
        average.append(option.NPV())

        # Bjerksund-Stensland Model
        option.setPricingEngine(ql.BjerksundStenslandApproximationEngine(process))
        results.append(("Bjerksund-Stensland", option.NPV()))
        average.append(option.NPV())

        # Finite-difference Model
        timeSteps = 801
        gridPoints = 800
        option.setPricingEngine(ql.FdBlackScholesVanillaEngine(process, timeSteps, gridPoints))
        results.append(("Finite differences", option.NPV()))
        average.append(option.NPV())

        # Binomial Model
        timeSteps = 801
        for tree in ["JR", "CRR", "EQP", "Trigeorgis", "Tian", "LR", "Joshi4"]:
            option.setPricingEngine(ql.BinomialVanillaEngine(process, tree, timeSteps))
            results.append(("Binomial (%s)" % tree, option.NPV()))
            average.append(option.NPV())

        price = sum(average) / len(average)

        return price

    # results as table
    def option_table(self):
        day_range = None
        float_range = None
        row_title = []
        f = int(self.stock_floats * 100)
        temp = pd.DataFrame()

        # check the days range
        if self.days_to_holds % 7 == 0:
            day_range = range(0, self.days_to_holds + 7, 7)
        elif self.days_to_holds <= 10:
            day_range = range(0, self.days_to_holds + 1, 1)
        elif 10 < self.days_to_holds <= 30:
            day_range = range(0, self.days_to_holds + 2, 2)
        elif 30 < self.days_to_holds <= 50:
            day_range = range(0, self.days_to_holds + 5, 5)
        elif 50 < self.days_to_holds <= 100:
            day_range = range(0, self.days_to_holds + 10, 10)
        elif 100 < self.days_to_holds <= 200:
            day_range = range(0, self.days_to_holds + 20, 20)

        # check the float range
        if f <= 10:
            float_range = range(-f, f + 1, 1)
        elif 10 < f <= 30:
            float_range = range(-f, f + 2, 2)
        elif 30 < f <= 50:
            float_range = range(-f, f + 5, 5)
        elif 50 < f <= 100:
            float_range = range(-f, f + 10, 10)

        for i in day_range:
            price = []
            self.days_to_holds = i

            for j in float_range:
                self.stock_floats = float(j / 100)
                price.append(np.around(self.option_price(), decimals=2))
            temp[str(i)] = price

        for i in float_range:
            prices = self.stock_prices * (1 + float(i / 100))
            row_title.append("$" + str(format(prices, ".2f")) + "   " + str(i) + "% ")

        df = pd.DataFrame(temp)
        df = df.set_index([row_title])
        df = df.add_suffix(" days")

        return df






