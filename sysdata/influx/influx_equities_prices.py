from sysdata.equities.equities_prices import equitiesPricesData
from sysdata.influx.influx_connection import InfluxData
from syslogdiag.log_to_screen import logtoscreen
from sysobjects.equities_prices import equitiesPrices


COLLECTION_NAME = 'alphavantage'

class influxEquitiesPricesData(equitiesPricesData):

    def __init__(self, influxdb=None, log=logtoscreen("influxEquitiesAdjustedPrices")):
        
        super(influxEquitiesPricesData, self).__init__(log=log)
        self._influx = InfluxData(COLLECTION_NAME)

    def __repr__(self):
        return repr(self._influx)

    def get_list_of_equities_codes(self) -> list:
        return self._influx.get_keynames()

    def get_equities_prices(self, code: str, start=None) -> equitiesPrices:
        return equitiesPrices(self._influx.read(code, start))