from sysdata.base_data import baseData
from sysobjects.equities_prices import equitiesPrices


USE_CHILD_CLASS_ERROR = "You need to use a child class of equitiesPricesData"

class equitiesPricesData(baseData):

    def __repr__(self):
        return USE_CHILD_CLASS_ERROR

    def __getitem__(self, keyname):
        return self.get_equities_prices(keyname)

    def keys(self):
        return self.get_list_of_equities_codes()

    def get_list_of_equities_codes(self):
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)

    def get_equities_prices(self, code: str) -> equitiesPrices:
        raise NotImplementedError(USE_CHILD_CLASS_ERROR)
 

