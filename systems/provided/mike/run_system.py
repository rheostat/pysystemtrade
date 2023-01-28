from systems.basesystem import System
from systems.positionsizing import PositionSizing
from systems.forecast_combine import ForecastCombine
from systems.forecast_scale_cap import ForecastScaleCap
from systems.trading_rules import TradingRule
from systems.forecasting import Rules
from systems.accounts.accounts_stage import Account
from systems.portfolio import Portfolios
from systems.rawdata import RawData
from systems.provided.mike.rules import rules
# from systems.provided.rules.ewmac import ewmac, ewmac_calc_vol
# from systems.provided.rules.breakout import breakout
# from systems.provided.rules.accel import accel
from sysdata.sim.db_equities_sim_data import dbEquitiesSimData
from sysdata.config.configdata import Config
from IPython import display

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import math


# rules = Rules(dict(
#     mac4 = TradingRule(ewmac, ['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'], {'Lfast':4, 'Lslow':16}),
#     mac8 = TradingRule(ewmac, ['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'], {'Lfast':8, 'Lslow':32}),
#     mac16 = TradingRule(ewmac, ['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'], {'Lfast':16, 'Lslow':64}),
#     mac32 = TradingRule(ewmac, ['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'], {'Lfast':32, 'Lslow':128}),
#     mac64 = TradingRule(ewmac, ['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'], {'Lfast':64, 'Lslow':256}),

#     normmom2 = TradingRule(ewmac_calc_vol, ['rawdata.get_cumulative_daily_vol_normalised_returns'], {'Lfast':2, 'Lslow':8}),
#     normmom4 = TradingRule(ewmac_calc_vol, ['rawdata.get_cumulative_daily_vol_normalised_returns'], {'Lfast':4, 'Lslow':16}),
#     normmom8 = TradingRule(ewmac_calc_vol, ['rawdata.get_cumulative_daily_vol_normalised_returns'], {'Lfast':8, 'Lslow':32}),
#     normmom16 = TradingRule(ewmac_calc_vol, ['rawdata.get_cumulative_daily_vol_normalised_returns'], {'Lfast':16, 'Lslow':64}),
#     normmom32 = TradingRule(ewmac_calc_vol, ['rawdata.get_cumulative_daily_vol_normalised_returns'], {'Lfast':32, 'Lslow':128}),
#     normmom64 = TradingRule(ewmac_calc_vol, ['rawdata.get_cumulative_daily_vol_normalised_returns'], {'Lfast':64, 'Lslow':256}),
    
#     breakout10 = TradingRule(breakout, [], {'lookback':10}),
#     breakout20 = TradingRule(breakout, [], {'lookback':20}),
#     breakout40 = TradingRule(breakout, [], {'lookback':40}),
#     breakout80 = TradingRule(breakout, [], {'lookback':80}),
#     breakout160 = TradingRule(breakout, [], {'lookback':160}),
#     breakout320 = TradingRule(breakout, [], {'lookback':320}),

#     accel16 = TradingRule(accel, ['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'], {'Lfast':16}),
#     accel32 = TradingRule(accel, ['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'], {'Lfast':32}),
#     accel64 = TradingRule(accel, ['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'], {'Lfast':64}),
# ))


def align_yaxis(ax1, ax2):
    """Align zeros of the two axes, zooming them out by same ratio"""
    axes = (ax1, ax2)
    extrema = [ax.get_ylim() for ax in axes]
    tops = [extr[1] / (extr[1] - extr[0]) for extr in extrema]
    # Ensure that plots (intervals) are ordered bottom to top:
    if tops[0] > tops[1]:
        axes, extrema, tops = [list(reversed(l)) for l in (axes, extrema, tops)]

    # How much would the plot overflow if we kept current zoom levels?
    tot_span = tops[1] + 1 - tops[0]

    b_new_t = extrema[0][0] + tot_span * (extrema[0][1] - extrema[0][0])
    t_new_b = extrema[1][1] - tot_span * (extrema[1][1] - extrema[1][0])
    axes[0].set_ylim(extrema[0][0], b_new_t)
    axes[1].set_ylim(t_new_b, extrema[1][1])


class MyPositionSizing(PositionSizing):

    def __init__(self, *args, long_only=False, **kwargs):
        self.__long_only = long_only
        super().__init__(*args, **kwargs)

    def get_subsystem_position(self, instrument_code: str) -> pd.Series:
        subsystem_position = super().get_subsystem_position(instrument_code)
        if self.__long_only:
            subsystem_position[subsystem_position < 0] = 0
        return subsystem_position

class MySystem:

    def __init__(self, name, config=Config(), long_only=False):
        system = System([rules, RawData(), ForecastScaleCap(), ForecastCombine(), MyPositionSizing(long_only=long_only), Account(), Portfolios()], data=dbEquitiesSimData(), config=config)
        # system.config.start_date = start_date
        system.config.notional_trading_capital = 1000000
        system.config.percentage_vol_target = 24
        # system.config.instrument_weights = instrument_weights
        # system.config.instrument_div_multiplier = 1.9
        # system.config.use_instrument_div_mult_estimates = True
        # system.config.use_instrument_weight_estimates = True
        # system.config.use_forecast_scale_estimates = True
        # system.config.use_forecast_div_mult_estimates = True
        # system.config.use_forecast_weight_estimates = True
        system.config.capital_multiplier['func'] = 'syscore.capital.full_compounding'
        print(system.get_instrument_list())
        self.system = system
        self.name = name


    def plot_combined_forecasts(self):


        n_instruments = len(self.system.get_instrument_list())
        dim = 6
        pos = (math.ceil(n_instruments/dim), dim)

        fig, ax = plt.subplots(*pos)
        for i, instrument in enumerate(self.system.get_instrument_list()):
            axis = ax[i//dim][i%dim] if pos[0] > 1 else ax[i%dim]
            axis.set_title(instrument)
            self.system.combForecast.get_combined_forecast(instrument).plot(ax=axis, lw=3)

        plt.tight_layout()
        plt.show()


    def plot_forecast_histogram(self, lookbacks=[-1, -6, -21]):

        forecasts = {}
        for instrument in self.system.get_instrument_list():
            forecasts[instrument] = self.system.combForecast.get_combined_forecast(instrument)

        forecasts = { k:[v[i] for i in lookbacks] for k,v in sorted(forecasts.items(), key=lambda item: item[1][-1]) }

        labels = list(forecasts.keys())
        values = list(forecasts.values())
        width = 0.2
        group_width = width * len(values[0])

        fig, ax = plt.subplots()
        
        for i in range(len(values[0])):
            x = np.arange(len(labels)) + group_width/2 - width/2 - width*i
            y = [a[i] for a in values]
            ax.bar(x, y, width, label=f'{lookbacks[i]+1} days')

        ax.set_xticks(x, labels)
        ax.legend()


    def plot_account_curves(self):
        portfolio = self.system.accounts.portfolio_with_multiplier()
        fig, ax1 = plt.subplots()
        portfolio.percent.curve().plot(ax=ax1, color='orange')
        portfolio.percent.drawdown().plot(ax=ax1, color='red')
        ax2 = ax1.twinx()
        portfolio.curve().plot(ax=ax2)

        align_yaxis(ax1,ax2)
        # ax1.set_yticks(step=25)
        ax1.minorticks_on()
        plt.show()

    def display_stats(self):
        display(self.system.accounts.portfolio().percent.stats())

    def get_weights(self):
        def get_percent_portfolio_weight(instrument):
            return self.system.accounts.get_buffered_position_with_multiplier(instrument)*self.system.data.daily_prices(instrument)/self.system.accounts.get_actual_capital()

        weights = pd.DataFrame()
        for i in self.system.get_instrument_list():
            weights[i] = get_percent_portfolio_weight(i)

        return weights

    def display_weights(self):
        display(self.get_weights())

    def write_ibkr_rebalance_file(self):
        from sysbrokers.IB.utils import write_ibkr_rebalance_file
        weights = self.get_weights()
        current_weights = {k:v for k,v in zip(weights.columns, weights[-1:].values[0])}
        current_weights

        write_ibkr_rebalance_file(self.name, current_weights, leverage=1)
