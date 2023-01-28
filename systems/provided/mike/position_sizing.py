from systems.positionsizing import PositionSizing
import pandas as pd

class MyPositionSizing(PositionSizing):

    def __init__(self, *args, long_only=False, **kwargs):
        self.__long_only = long_only
        super().__init__(*args, **kwargs)

    def get_subsystem_position(self, instrument_code: str) -> pd.Series:
        subsystem_position = super().get_subsystem_position(instrument_code)
        if self.__long_only:
            subsystem_position[subsystem_position < 0] = 0
        return subsystem_position