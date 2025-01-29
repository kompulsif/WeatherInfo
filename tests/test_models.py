import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from platform import system
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from models import Day, Station, WeatherResponse
from weather import Weather


@pytest.fixture
def weather() -> Weather:
    # return Weather object
    return Weather()

@pytest.fixture
def getIpData() -> Dict[str, str]:
    return {
        "ip": "123.123.123.123",
        "hostname": "hostname.comunity",
        "city": "Ankara",
        "region": "Ankara",
        "country": "TR",
        "loc": "39.9272,32.8644",
        "org": "Turk Telekom",
        "postal": "t-postal:06636",
        "timezone": "Europe/Istanbul"
}
    

@pytest.fixture
def getStationData() -> Dict[str, Any]:
    # Api Response Data: Station
    return {
        "distance": 22252.0,
        "latitude": 39.9272,
        "longitude": 32.8644,
        "useCount": 0,
        "id": "LTAC",
        "name": "LTAC",
        "quality": 50,
        "contribution": 0.0,
    }


@pytest.fixture
def getDayData() -> Dict[str, Any]:
    # Api Response Data: Day
    return {
        "datetime": "2025-01-27",
        "datetimeEpoch": 1737925200,
        "tempmax": 45.5,
        "tempmin": 27.8,
        "temp": 34.4,
        "feelslikemax": 42,
        "feelslikemin": 27.8,
        "feelslike": 33.4,
        "dew": 31.7,
        "humidity": 90.6,
        "precip": 0,
        "precipprob": 0,
        "precipcover": 0,
        "preciptype": None,
        "snow": 0,
        "snowdepth": 0,
        "windgust": 7.8,
        "windspeed": 6.9,
        "winddir": 193.1,
        "pressure": 1024.1,
        "cloudcover": 77.9,
        "visibility": 4.3,
        "solarradiation": 135.7,
        "solarenergy": 11.6,
        "uvindex": 5,
        "severerisk": 10,
        "sunrise": "08:01:16",
        "sunriseEpoch": 1737954076,
        "sunset": "18:01:55",
        "sunsetEpoch": 1737990115,
        "moonphase": 0.93,
        "conditions": "Partially cloudy",
        "description": "Partly cloudy throughout the day.",
        "icon": "partly-cloudy-day",
        "stations": ["LTAC", "LTAB", "LTAE"],
        "source": "comb",
    }


@pytest.fixture
def getResponseData(
    # Response Api Request
    getDayData: Dict[str, Any],
    getStationData: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "queryCost": 1,
        "latitude": 39.9272,
        "longitude": 32.8644,
        "resolvedAddress": "39.927200,32.864400",
        "address": "39.927200,32.864400",
        "timezone": "Europe/Istanbul",
        "tzoffset": 3,
        "days": [Day(**getDayData)],
        "stations": {"LTAC": Station(**getStationData)},
    }


def test_station_class(getStationData: Dict[str, Any]) -> None:
    # test Station Pydantic Base Model
    station = Station(**getStationData)
    assert station.distance == 22252.0
    assert station.latitude == 39.9272
    assert station.longitude == 32.8644
    assert station.useCount == 0
    assert station.id == "LTAC"
    assert station.name == "LTAC"
    assert station.quality == 50
    assert station.contribution == 0.0


def test_day_class(getDayData: Dict[str, Any]) -> None:
    # test Day Pydantic Base Model
    day = Day(**getDayData)

    assert day.datetime == "2025-01-27"
    assert day.datetimeEpoch == 1737925200
    assert day.tempmax == 45.5
    assert day.tempmin == 27.8
    assert day.temp == 34.4
    assert day.feelslikemax == 42
    assert day.feelslikemin == 27.8
    assert day.feelslike == 33.4
    assert day.dew == 31.7
    assert day.humidity == 90.6
    assert day.precip == 0
    assert day.precipprob == 0
    assert day.precipcover == 0
    assert day.preciptype is None
    assert day.snow == 0
    assert day.snowdepth == 0
    assert day.windgust == 7.8
    assert day.windspeed == 6.9
    assert day.winddir == 193.1
    assert day.pressure == 1024.1
    assert day.cloudcover == 77.9
    assert day.visibility == 4.3
    assert day.solarradiation == 135.7
    assert day.solarenergy == 11.6
    assert day.uvindex == 5
    assert day.severerisk == 10
    assert day.sunrise == "08:01:16"
    assert day.sunriseEpoch == 1737954076
    assert day.sunset == "18:01:55"
    assert day.sunsetEpoch == 1737990115
    assert day.moonphase == 0.93
    assert day.conditions == "Partially cloudy"
    assert day.description == "Partly cloudy throughout the day."
    assert day.icon == "partly-cloudy-day"
    assert day.stations == ["LTAC", "LTAB", "LTAE"]


def test_wheatherResponse_class(
    getDayData: Dict[str, Any],
    getStationData: Dict[str, Any],
    getResponseData: Dict[str, Any],
) -> None:
    # test WeatherResponse Pydantic Base Model
    wres = WeatherResponse(**getResponseData)
    assert wres.queryCost == 1
    assert wres.latitude == 39.9272
    assert wres.longitude == 32.8644
    assert wres.resolvedAddress == "39.927200,32.864400"
    assert wres.address == "39.927200,32.864400"
    assert wres.timezone == "Europe/Istanbul"
    assert wres.tzoffset == 3
    assert wres.days == [Day(**getDayData)]
    assert wres.stations == {"LTAC": Station(**getStationData)}


def test_unit_symbol(weather: Weather) -> None:
    # test getUnitSymbol method
    symbol: str = weather.getUnitSymbol()
    assert symbol == "°C"

    weather.unitg = "us"
    symbol: str = weather.getUnitSymbol()
    assert symbol == "°F"

    weather.unitg = "uk"
    symbol: str = weather.getUnitSymbol()
    assert symbol == "°C"

    weather.unitg = "base"
    symbol: str = weather.getUnitSymbol()
    assert symbol == "K"


@patch("requests.get")
def test_api_response(mock_get, getResponseData: Dict[str, Any]) -> None:
    # test __getWeatherData method

    import requests as r

    mock_rs = MagicMock()
    mock_rs.json.return_value = getResponseData
    mock_get.return_value = mock_rs
    
    rs: Dict[str, Any] = r.get(
        "https://weather.visualcrossing.com/api/test-request"
    )
    assert rs.json() == getResponseData


@patch("winsdk.windows.devices.geolocation.Geolocator", autospec=True)
def test_location_by_gps(mock_geolocation) -> None:
    if system() == "Windows":
        
        import winsdk.windows.devices.geolocation as t
        
        mock_pos = MagicMock()
        mock_pos.coordinate.latitude = 39.927200
        mock_pos.coordinate.longitude = 32.864400
        
        mock_geolocation.get_geoposition_async.return_value = mock_pos
        mock_geolocation.return_value = mock_geolocation
        
        g = t.Geolocator().get_geoposition_async()
        assert g.coordinate.latitude == 39.927200
        assert g.coordinate.longitude == 32.864400
        
    else:
        raise TypeError("Your operating system is not suitable for this test. Must be windows")


@patch("requests.get")
def test_location_by_ip(mock_get, getIpData: Dict[str, str]) -> None:
    
    res_mock = MagicMock()
    res_mock.json.return_value = getIpData
    
    mock_get.return_value = res_mock
    
    import requests
    
    r = requests.get("https://ipinfo.io/json?token=test")
    assert r.json() == getIpData