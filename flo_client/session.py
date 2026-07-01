from abc import ABC, abstractmethod

from flo_client.consts import *

class Session(ABC, dict):

    def __init__(self, session: dict):
        super().__init__(session)

    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @property
    @abstractmethod
    def station_id(self) -> str:
        pass

    @property
    @abstractmethod
    def is_vehicle_charging(self) -> bool:
        pass

    @property
    @abstractmethod
    def amperage(self) -> float:
        pass

    @property
    @abstractmethod
    def amperage_offered(self) -> float:
        pass

    @property
    @abstractmethod
    def voltage(self) -> float:
        pass

    @property
    @abstractmethod
    def energy_transfered_kwh(self) -> float:
        pass


class Sessionv30(Session):
    def __init__(self, session: dict):
        super().__init__(session)

    @property
    def id(self) -> str:
        return (self[SESSION_ID] if SESSION_ID in self else "")

    @property
    def station_id(self) -> str:
        return (self["station"]["id"] if "station" in self and "id" in self["station"] else "")

    @property
    def is_vehicle_charging(self) -> bool:
        return self[SESSION_STATE_KEY] == SESSION_CHARGING

    @property
    def amperage(self) -> float:
        return float(self[SESSION_AMPERAGE])

    @property
    def amperage_offered(self) -> float:
        return float(self[SESSION_AMPERAGE_OFFERED])

    @property
    def voltage(self) -> float:
        return float(self[SESSION_VOLTAGE])

    @property
    def energy_transfered_kwh(self) -> float:
        return float(self[SESSION_ENERGY_TRANSFERRED_WH]) / 1000.0

class Sessionv31(Sessionv30):
    #Sessions in API version 3.1 are the same as in version 3.0, so we can just inherit from Sessionv30.

    def __init__(self, session: dict):
        super().__init__(session)
