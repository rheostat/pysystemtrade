
from syscore.objects import arg_not_supplied

from sysdata.sim.db_equities_sim_data import dbEquitiesSimData
from sysdata.config.configdata import Config

from systems.basesystem import System
from systems.forecast_combine import ForecastCombine
from systems.rawdata import RawData
from systems.forecast_scale_cap import ForecastScaleCap
from systems.accounts.accounts_stage import Account


# from systems.provided.rob_system.forecastScaleCap import volAttenForecastScaleCap
# from systems.provided.rob_system.rawdata import myFuturesRawData
# from systems.positionsizing import PositionSizing
from systems.portfolio import Portfolios

# from systems.provided.dynamic_small_system_optimise.optimised_positions_stage import (
#     optimisedPositions,
# )
# from systems.risk import Risk
# from systems.provided.dynamic_small_system_optimise.accounts_stage import (
#     accountForOptimisedStage,
# )

from systems.provided.mike.rules import rules
from systems.provided.mike.position_sizing import MyPositionSizing

def make_system(
    sim_data=arg_not_supplied, config_filename="systems.provided.mike.config.yaml", long_only=True
):

    if sim_data is arg_not_supplied:
        sim_data = dbEquitiesSimData()

    config = Config(config_filename)

    system = System(
        [
            rules, RawData(), ForecastScaleCap(), ForecastCombine(), MyPositionSizing(long_only=long_only), Account(), Portfolios()
            # Risk(),
            # accountForOptimisedStage(),
            # optimisedPositions(),
            # Portfolios(),
            # PositionSizing(),
            # myFuturesRawData(),
            # ForecastCombine(),
            # volAttenForecastScaleCap(),
            # rules,
        ],
        sim_data,
        config,
    )
    system.set_logging_level("terse")

    return system

