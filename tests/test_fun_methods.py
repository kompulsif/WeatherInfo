import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from platform import system
from typing import Any, Dict

import pytest

from models import Day, Station, WeatherResponse
from weather import Weather


@pytest.fixture
def weather() -> Weather:
    # return Weather object
    return Weather()


@pytest.fixture
def getIpData() -> Dict[str, str]:
    # api Response Data by Ip
    return {
        "ip": "123.123.123.123",
        "hostname": "hostname.comunity",
        "city": "Ankara",
        "region": "Ankara",
        "country": "TR",
        "loc": "39.9272,32.8644",
        "org": "Turk Telekom",
        "postal": "t-postal:06636",
        "timezone": "Europe/Istanbul",
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
    # Response Weather Api Request
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


def test_weather_api_response(mocker, getResponseData: Dict[str, Any]) -> None:
    # test __getWeatherData method
    mock_rs = mocker.patch("requests.get")
    mock_rs.return_value.json.return_value = getResponseData

    import requests as r

    r: Dict[str, Any] = r.get(
        "https://weather.visualcrossing.com/api/test-request"
    ).json()

    assert (
        len(
            list(
                filter(
                    lambda x: x in r.keys(),
                    [
                        "queryCost",
                        "latitude",
                        "longitude",
                        "resolvedAddress",
                        "address",
                        "timezone",
                        "tzoffset",
                        "days",
                        "stations",
                    ],
                )
            )
        )
        == 9
    )

    assert r["queryCost"] == 1
    assert r["latitude"] == 39.9272
    assert r["longitude"] == 32.8644
    assert r["resolvedAddress"] == "39.927200,32.864400"
    assert r["address"] == "39.927200,32.864400"
    assert r["timezone"] == "Europe/Istanbul"
    assert r["tzoffset"] == 3
    assert len(r["days"]) >= 1 and len(
        list(filter(lambda x: isinstance(x, Day), r["days"]))
    ) == len(r["days"])
    assert len(r["stations"]) >= 1 and len(
        list(filter(lambda x: isinstance(x, Station), r["stations"].values()))
    ) == len(r["stations"])


def test_location_by_gps(mocker) -> None:
    # test Weather __getCoordinatesByGPS
    if system() != "Windows":
        mock_pos = mocker.MagicMock()
        mock_pos.coordinate.latitude = 39.927200
        mock_pos.coordinate.longitude = 32.864400

        import winsdk.windows.devices.geolocation as t

        mock_geolocation = mocker.patch("winsdk.windows.devices.geolocation.Geolocator")
        mock_geolocation.return_value.get_geoposition_async.return_value = mock_pos

        g = t.Geolocator().get_geoposition_async()
        assert g.coordinate.latitude == 39.927200
        assert g.coordinate.longitude == 32.864400

    else:
        pytest.skip(
            "test_location_by_ip test will be suitable for your operating system."
        )


def test_location_by_ip(mocker, getIpData: Dict[str, str]) -> None:
    # test Weather __getCoordinatesByIP
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.return_value = getIpData

    import requests

    r: Dict[str, str] = requests.get("https://ipinfo.io/json?token=test").json()

    assert (
        len(
            list(
                filter(
                    lambda x: x in r.keys(),
                    [
                        "ip",
                        "hostname",
                        "city",
                        "region",
                        "country",
                        "loc",
                        "org",
                        "postal",
                        "timezone",
                    ],
                )
            )
        )
        == 9
    )
    assert r["ip"] == "123.123.123.123"
    assert r["hostname"] == "hostname.comunity"
    assert r["city"] == "Ankara"
    assert r["region"] == "Ankara"
    assert r["country"] == "TR"
    assert r["loc"] == "39.9272,32.8644"
    assert r["org"] == "Turk Telekom"
    assert r["postal"] == "t-postal:06636"
    assert r["timezone"] == "Europe/Istanbul"
