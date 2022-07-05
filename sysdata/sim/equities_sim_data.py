from sysdata.sim.sim_data import simData
from sysobjects.instruments import instrumentCosts
from sysobjects.spot_fx_prices import fxPrices


import pandas as pd
import datetime


class equitiesSimData(simData):

    def __init__(self, data):
        super().__init__(log=data.log)
        self._data = data

    # def __repr__(self):
    #     return "equitiesSimData object %d instruments" % len(
    #         self.get_instrument_list()
    #     )

    @property
    def data(self):
        return self._data

    def get_instrument_list(self) -> list:
        return self.data.db_equities_prices.get_list_of_equities_codes()

    def get_raw_price_from_start_date(self, instrument_code: str, start_date: datetime.datetime) -> pd.Series:
        return self.data.db_equities_prices.get_equities_prices(instrument_code, start_date).adjusted_close

    def get_instrument_currency(self, instrument_code: str) -> str:
        return 'USD'

    def _get_fx_data_from_start_date(
        self, currency1: str, currency2: str, start_date
    ) -> fxPrices:
        fx_code = currency1 + currency2
        data = self.data.db_fx_prices.get_fx_prices(fx_code)

        data_after_start = data[start_date:]

        return data_after_start

    def get_value_of_block_price_move(self, instrument_code: str) -> float:
        return 1.0

    def get_raw_cost_data(self, instrument_code: str) -> instrumentCosts:
        return instrumentCosts()

