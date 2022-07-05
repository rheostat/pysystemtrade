"""
Get data from influx for equities trading

"""
from syscore.objects import arg_not_supplied
from sysdata.influx.influx_equities_prices import influxEquitiesPricesData
from sysdata.csv.csv_spot_fx import csvFxPricesData


from sysdata.sim.equities_sim_data import equitiesSimData
from sysdata.data_blob_with_influx import dataBlobWithInflux

from syslogdiag.log_to_screen import logtoscreen

class dbEquitiesSimData(equitiesSimData):
    def __init__(
        self, data: dataBlobWithInflux = arg_not_supplied, log=logtoscreen("dbEquitiesSimData")
    ):

        if data is arg_not_supplied:
            data = dataBlobWithInflux(
                log=log,
                class_list=[
                    influxEquitiesPricesData,
                    csvFxPricesData,
                ],
            )

        super(dbEquitiesSimData, self).__init__(data=data)

    # def __repr__(self):
    #     return "dbEquitiesSimData object with %d instruments" % len(
    #         self.get_instrument_list()
    #     )


if __name__ == '__main__':

    data = dbEquitiesSimData()
    print(dir(data.data))
    equities_prices = data.data.db_equities_prices
    print(dir(equities_prices))
    print(equities_prices.get_list_of_equities_codes()[:10])
