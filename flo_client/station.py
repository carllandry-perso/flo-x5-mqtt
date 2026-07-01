from abc import ABC, abstractmethod

from flo_client.consts import *

class Station(ABC, dict):

    def __init__(self, station: dict):
        super().__init__(station)

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @property
    @abstractmethod
    def vendor(self) -> str:
        pass

    @property
    @abstractmethod
    def model(self) -> str:
        pass

    @property
    @abstractmethod
    def is_online(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_vehicle_connected(self) -> bool:
        pass

class Stationv30(Station):
    def __init__(self, station: dict):
        super().__init__(station)

    @property
    def name(self) -> str:
        return (self["information"]["name"] if "information" in self and "name" in self["information"] else "")

    @property
    def id(self) -> str:
        return (self["information"]["id"] if "information" in self and "id" in self["information"] else "")

    @property
    def vendor(self) -> str:
        return ("flo")

    @property
    def model(self) -> str:
        return ("X5")

    @property
    def is_online(self) -> bool:
        return (
            self[STATUS_KEY][STATE_KEY] == STATE_AVAILABLE
            or self[STATUS_KEY][STATE_KEY] == STATE_INUSE
        )

    @property
    def is_vehicle_connected(self) -> bool:
        return (
            self[STATUS_KEY][PILOT_STATE_KEY] == PILOT_STATE_CONNECTED
            or self[STATUS_KEY][PILOT_STATE_KEY] == PILOT_STATE_CHARGING
        )

class Stationv31(Station):
    def __init__(self, station: dict):
        super().__init__(station)

    @property
    def name(self) -> str:
        return (self["physicalReference"] if "physicalReference" in self else "")

    @property
    def id(self) -> str:
        return (self["chargingStationUid"] if "chargingStationUid" in self else "")

    @property
    def vendor(self) -> str:
        return (self["vendor"] if "vendor" in self else "")

    @property
    def model(self) -> str:
        return (self["modelType"] if "modelType" in self else "")

    @property
    def is_online(self) -> bool:
        return (
            self[CONNECTION_STATUS_KEY] == STATE_ONLINE
        )

    @property
    def is_vehicle_connected(self) -> bool:
        return (
            self[USE_KEY][STATUS_KEY] == SESSION_COMPLETED
            or self[USE_KEY][STATUS_KEY] == SESSION_CHARGING
        )
