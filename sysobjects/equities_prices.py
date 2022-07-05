import pandas as pd

PRICE_DATA_COLUMNS = sorted(['open', 'high', 'low', 'close', 'adjusted_close', 'dividend', 'split_coefficient', 'volume'])
CLOSE_COLUMN = 'close'
ADJUSTED_CLOSE_COLUMN = 'adjusted_close'
VOLUME_COLUMN = 'volume'

class equitiesPrices(pd.DataFrame):

    def __init__(self, price_data_as_df: pd.DataFrame):
        """

        :param data: pd.DataFrame or something that could be passed to it
        """

        _validate_price_data(price_data_as_df)
        price_data_as_df.index.name = "index"  # for arctic compatibility
        super().__init__(price_data_as_df)

        self._as_df = price_data_as_df

    @classmethod
    def create_empty(equityPrices):
        """
        Our graceful fail is to return an empty, but valid, dataframe
        """

        data = pd.DataFrame(columns=PRICE_DATA_COLUMNS)

        equity_prices = equitiesPrices(data)

        return equity_prices

    def closing_prices(self):
        return equitiesClosingPrices(self[CLOSE_COLUMN])

    def adjusted_closing_prices(self):
        return equitiesAdjustedClosingPrices(self[ADJUSTED_CLOSE_COLUMN])

    def daily_volumes(self) -> pd.Series:
        return self[VOLUME_COLUMN]


class equitiesClosingPrices(pd.Series):

    def __init__(self, data):
        super(equitiesClosingPrices, self).__init__(data)


class equitiesAdjustedClosingPrices(pd.Series):

    def __init__(self, data):
        super(equitiesAdjustedClosingPrices, self).__init__(data)


def _validate_price_data(data: pd.DataFrame):
    data_present = sorted(data.columns)

    try:
        assert data_present == PRICE_DATA_COLUMNS
    except AssertionError:
        raise Exception("equityPrices has to conform to pattern")