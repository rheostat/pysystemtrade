from systems.forecasting import Rules
from systems.trading_rules import TradingRule
from systems.provided.rules.ewmac import ewmac
from systems.provided.rules.breakout import breakout
from systems.provided.rules.accel import accel


def neg_skew(price, lookback):
    result = price.pct_change().rolling(lookback).skew()
    return -result

def kurtosis(price, lookback):
    result = price.pct_change().rolling(lookback).kurt()
    return result


rules = Rules(dict(
    # mac4 = TradingRule(ewmac, ['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'], {'Lfast':4, 'Lslow':16}),
    mac8 = TradingRule(ewmac, ['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'], {'Lfast':8, 'Lslow':32}),
    mac16 = TradingRule(ewmac, ['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'], {'Lfast':16, 'Lslow':64}),
    mac32 = TradingRule(ewmac, ['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'], {'Lfast':32, 'Lslow':128}),
    mac64 = TradingRule(ewmac, ['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'], {'Lfast':64, 'Lslow':256}),

    # normmom2 = TradingRule(ewmac_calc_vol, ['rawdata.get_cumulative_daily_vol_normalised_returns'], {'Lfast':2, 'Lslow':8}),
    # normmom4 = TradingRule(ewmac_calc_vol, ['rawdata.get_cumulative_daily_vol_normalised_returns'], {'Lfast':4, 'Lslow':16}),
    # normmom8 = TradingRule(ewmac_calc_vol, ['rawdata.get_cumulative_daily_vol_normalised_returns'], {'Lfast':8, 'Lslow':32}),
    # normmom16 = TradingRule(ewmac_calc_vol, ['rawdata.get_cumulative_daily_vol_normalised_returns'], {'Lfast':16, 'Lslow':64}),
    # normmom32 = TradingRule(ewmac_calc_vol, ['rawdata.get_cumulative_daily_vol_normalised_returns'], {'Lfast':32, 'Lslow':128}),
    # normmom64 = TradingRule(ewmac_calc_vol, ['rawdata.get_cumulative_daily_vol_normalised_returns'], {'Lfast':64, 'Lslow':256}),
    
    breakout16 = TradingRule(breakout, [], {'lookback':16}),
    breakout32 = TradingRule(breakout, [], {'lookback':32}),
    breakout64 = TradingRule(breakout, [], {'lookback':64}),
    breakout128 = TradingRule(breakout, [], {'lookback':128}),
    breakout256 = TradingRule(breakout, [], {'lookback':256}),

    accel16 = TradingRule(accel, ['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'], {'Lfast':16}),
    accel32 = TradingRule(accel, ['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'], {'Lfast':32}),
    accel64 = TradingRule(accel, ['rawdata.get_daily_prices', 'rawdata.daily_returns_volatility'], {'Lfast':64}),

    neg_skew64 = TradingRule(neg_skew, ['rawdata.get_daily_prices'], {'lookback': 64}),
    neg_skew128 = TradingRule(neg_skew, ['rawdata.get_daily_prices'], {'lookback': 128}),
    neg_skew256 = TradingRule(neg_skew, ['rawdata.get_daily_prices'], {'lookback': 256}),

    kurt64 = TradingRule(kurtosis, ['rawdata.get_daily_prices'], {'lookback': 64}),
    kurt128 = TradingRule(kurtosis, ['rawdata.get_daily_prices'], {'lookback': 128}),
    kurt256 = TradingRule(kurtosis, ['rawdata.get_daily_prices'], {'lookback': 256}),
))
