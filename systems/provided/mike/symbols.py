def weight_group(*symbols, total_weight=1):
    weight = total_weight / len(symbols)
    return { s:weight for s in symbols }

instrument_weights = dict(
    **weight_group('SPY', 'QQQ', 'VYM', 'EEM'),
    **weight_group('AGG', 'SHY', 'IEF', 'TLT', 'LQD', 'HYG'),
    **weight_group('GLD', 'BITO', 'FXE', 'FXY', 'FXC'),
    **weight_group('PDBC'),
)
