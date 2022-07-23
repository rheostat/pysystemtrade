from syscore.objects import arg_not_supplied

from sysdata.sim.equities_sim_data import equitiesSimData
from sysdata.config.configdata import Config

from systems.forecasting import Rules
from systems.basesystem import System
from systems.forecast_combine import ForecastCombine
from systems.forecast_scale_cap import ForecastScaleCap
from systems.positionsizing import PositionSizing
from systems.portfolio import Portfolios
from systems.accounts.accounts_stage import Account


def equities_system(
    sim_data=arg_not_supplied, rules=[], config=Config()
):

    if sim_data is arg_not_supplied:
        sim_data = equitiesSimData()

    system = System(
        [
            Portfolios(),
            Account(),
            PositionSizing(),
            ForecastCombine(),
            ForecastScaleCap(),
            Rules(rules),
        ],
        sim_data,
        config,
    )
    system.set_logging_level("on")

    return system

