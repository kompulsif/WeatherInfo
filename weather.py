import asyncio
import json
import os
from argparse import ArgumentParser, Namespace
from typing import Any, Dict, List

import winsdk.windows.devices.geolocation as g
from dotenv import load_dotenv
from requests import Response, exceptions, get

from models import *  # noqa: F403

load_dotenv()

API_KEY: str = os.environ["API_KEY"]
QUERY: str = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{},{}/today?unitGroup={}&lang={}&key={}&contentType=json&include=days"
SYMBOLS: Dict[str, str] = {"metric": "°C", "us": "°F", "uk": "°C", "base": "K"}


class Weather:
    def __init__(
        self, coordinates: List[float] = [], lang: str = "tr", unitg: str = "metric"
    ) -> None:
        # If no coordinates are provided, get the coordinates using GPS.
        cs: List[float] = (
            asyncio.run(Weather.__getCoordinates())
            if (not coordinates)
            else coordinates
        )

        self.coordinates: List[float] = cs
        self.lang: str = lang
        self.unitg: str = unitg
        self.symbol: str = self.__getUnitSymbol()

    def showClearText(self) -> None:
        # Get weather data and print the maximum temperature and description.
        data: Dict[Any, Any] = self.__getWeatherData()

        weatherReponse: WeatherResponse = WeatherResponse(**data)  # noqa: F405
        temp: float = weatherReponse.days[0].tempmax
        description: str = weatherReponse.days[0].description

        print(
            f"{self.coordinates[0]},{self.coordinates[1]} | {temp}{self.symbol} -> {description}"
        )

    def __getUnitSymbol(self) -> str:
        # Return the unit symbol based on the unit group.
        try:
            return SYMBOLS[self.unitg]
        except Exception:
            print("Unit Group error!")
            exit()

    def __getWeatherData(self) -> Dict[Any, Any]:
        # Format the query URL and fetch weather data.
        formattedQuery: str = QUERY.format(
            self.coordinates[0], self.coordinates[1], self.unitg, self.lang, API_KEY
        )
        try:
            res: Response = get(formattedQuery)
            jsonData: Dict[Any, Any] = res.json()
        except exceptions.RequestException:
            print("Please check your internet connection or API key.")
            exit()
        except json.JSONDecodeError:
            print(
                "Response is not valid! Please check the connection and API key and try again.."
            )
            exit()
        except Exception:
            print("An error occurred while retrieving weather information!")
            exit()
        else:
            return jsonData

    @staticmethod
    async def __getCoordinates() -> List[float]:
        # Get the current device's GPS coordinates.
        locator: g.Geolocator = g.Geolocator()
        try:
            pos: g.Geoposition = await locator.get_geoposition_async()
        except PermissionError:
            print("Permission error! Please allow location access.")
            exit()
        except Exception:
            print("An error occurred while accessing the location!")
            exit()
        else:
            if pos.coordinate is not None:
                return [float(pos.coordinate.latitude), float(pos.coordinate.longitude)]
            else:
                print("Unable to fetch coordinates.")
                exit()


def getArguments() -> Namespace:
    # Parse command line arguments.
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument(
        "--coordinates",
        help="Coordinates: X,Y or GPS. Default is GPS.",
        default="gps",
        type=str,
    )
    parser.add_argument(
        "--language", help="Output language. Default is TR.", default="tr", type=str
    )
    parser.add_argument(
        "--unitGroup",
        help="Unit Groups: us, uk, metric, base. Default is metric.",
        default="metric",
        type=str,
    )
    return parser.parse_args()


if __name__ == "__main__":
    # Get arguments from the command line.
    args: Namespace = getArguments()
    csarg: str = args.coordinates
    lang: str = args.language.lower()
    unitG: str = args.unitGroup.lower()

    # If coordinates are provided in the command line, parse them.
    if csarg != "gps":
        try:
            if csarg.startswith("'") and csarg.endswith("'"):
                coordinates: List[float] = list(map(float, csarg[1:-1].split(",")))
            else:
                raise ValueError
        except Exception:
            print("Format of coordinates; should be 'latitude,longitude'")
            exit()
    else:
        coordinates = []

    # Create Weather object and show the weather information.
    weather: Weather = Weather(coordinates, lang, unitG)
    weather.showClearText()
