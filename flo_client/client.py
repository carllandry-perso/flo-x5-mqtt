"""Client for the flo X5 API."""

from abc import ABC, abstractmethod
import logging
import json
from typing import Optional
import requests

from datetime import datetime, timedelta

from flo_client.auth import Auth
from flo_client.consts import *
from flo_client.station import Station, Stationv30, Stationv31
from flo_client.session import Session, Sessionv30, Sessionv31

class FloX5Client(ABC):

    _auth: Optional[Auth] = None
    """Keeping a single _auth instance to avoid multiple logins when testing multiple API versions."""

    @classmethod
    def get_client(cls, username: str, password: str) -> "FloX5Client":
        #Try to initialize the client using the version 3.0
        # If it fails (not stations are found), fallback to the version 3.1 of the API
        clientv30 = FloX5Clientv30(username, password)

        if (clientv30._get_stations()):
            return clientv30

        clientv31 = FloX5Clientv31(username, password)

        #Not testing if the version 3.1 is successful.
        #This is compliant to the original implementation.
        return clientv31

    def __init__(self, username: str, password: str) -> None:
        self.next_refresh = datetime.now()

        if (not FloX5Client._auth):
            FloX5Client._auth = Auth(username, password)

        self._refresh()

    def _refresh(self) -> None:
        # Refresh every minutes at most
        if datetime.now() < self.next_refresh:
            return

        self._stations = self._get_stations()
        self._sessions = self._get_sessions()

        self.next_refresh = datetime.now() + timedelta(seconds=REFRESH_DELAY_SECS)

    @abstractmethod
    def _get_stations(self) -> list[Station]:
        pass

    @abstractmethod
    def get_station_by_name(self, name: str) -> Station | None:
        pass

    @abstractmethod
    def _get_sessions(self) -> list[Session]:
        pass

    @abstractmethod
    def get_session_by_station_id(self, id: str) -> Session | None:
        pass

    def _get_headers(self) -> dict:
        return {
            "Accept": "*/*",
            "Authorization": "Bearer " + FloX5Client._auth.get_access_token() if FloX5Client._auth else "",
        }


class FloX5Clientv30(FloX5Client):
    def __init__(self, username: str, password: str) -> None:
        super().__init__(username, password)

    def _get_stations(self) -> list[Station]:
        resp = requests.get(STATIONS_30_URL, headers=self._get_headers())
        if resp.status_code != 200:
            raise Exception("Error getting stations.", resp.status_code, resp.text)

        # Convert the result to a list of Station objects
        return [Stationv30(station_dict) for station_dict in resp.json()]

    def get_station_by_name(self, name: str) -> Station | None:
        self._refresh()
        for station in self._stations:
            if station.name == name:
                return station

        return None

    def _get_sessions(self) -> list[Session]:
        resp = requests.get(SESSIONS_30_URL, headers=self._get_headers())
        if resp.status_code != 200:
            raise Exception("Error getting sessions.", resp.status_code, resp.text)

        return [Sessionv30(session_dict) for session_dict in resp.json()]

    def get_session_by_station_id(self, id: str) -> Session | None:
        self._refresh()
        for session in self._sessions:
            if session.station_id == id:
                return session

        return None


class FloX5Clientv31(FloX5Client):
    def __init__(self, username: str, password: str) -> None:
        super().__init__(username, password)

    def _get_stations(self) -> list[Station]:
        resp = requests.get(STATIONS_31_URL, headers=self._get_headers())
        if resp.status_code != 200:
            raise Exception("Error getting stations.", resp.status_code, resp.text)

        # Convert the result to a list of Station objects
        #Version 3.1 has station under the "ocpiHomeStations" or "legacyHomeStations" key.
        #The "legacy" one is unknown and not used in the current implementation.
        ocpiHomeStations = resp.json().get("ocpiHomeStations", [])
        return [Stationv31(station_dict) for station_dict in ocpiHomeStations]

    def get_station_by_name(self, name: str) -> Station | None:
        self._refresh()
        for station in self._stations:
            if station.name == name:
                return station

        return None

    def _get_sessions(self) -> list[Session]:
        resp = requests.get(SESSIONS_31_URL, headers=self._get_headers())
        if resp.status_code != 200:
            raise Exception("Error getting sessions.", resp.status_code, resp.text)

        session = json.loads(resp.text)

        return session

    def get_session_by_station_id(self, id: str) -> Session | None:
        self._refresh()
        for session_dict in self._sessions:
            #Version 3.1 seems to use the same session structure as version 3.0.
            session = Sessionv31(session_dict)
            if session.station_id == id:
                return session

        return None
