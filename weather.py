import asyncio
import json
import os
from argparse import ArgumentParser
from logging import DEBUG, WARNING, Formatter, Handler, Logger, StreamHandler
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, List, Tuple

import winsdk.windows.devices.geolocation as g
from dotenv import load_dotenv
from requests import Response, exceptions, get

from models import *  # noqa: F403

load_dotenv()

API_KEY: str = os.environ["API_KEY"]
QUERY: str = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{},{}/today?unitGroup={}&lang={}&key={}&contentType=json&include=days"
SYMBOLS: Dict[str, str] = {"metric": "°C", "us": "°F", "uk": "°C", "base": "K"}
LOGGER: Logger = Logger(__name__)
FORMATTER_CONSOLE: Formatter = Formatter("%(levelname)s - %(message)s")
FORMATTER_FILE: Formatter = Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
FILE_HANDLER: RotatingFileHandler = RotatingFileHandler(
    filename="process_log.log", mode="a", maxBytes=50000
)
CONSOLE_HANDLER: Handler = StreamHandler()


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
        LOGGER.debug(f"Coordinates to use(variable -> cs): {cs}")
        self.coordinates: List[float] = cs
        self.lang: str = lang
        self.unitg: str = unitg
        self.symbol: str = self.__getUnitSymbol()

    def showClearText(self) -> None:
        # Get weather data and print the maximum temperature and description.
        data: Dict[Any, Any] = self.__getWeatherData()
        LOGGER.info("Weather data received")
        weatherReponse: WeatherResponse = WeatherResponse(**data)  # noqa: F405
        temp: float = weatherReponse.days[0].tempmax
        description: str = weatherReponse.days[0].description

        print(
            f"\n\n{self.coordinates[0]},{self.coordinates[1]} | {temp}{self.symbol} -> {description}\n\n"
        )

    def __getUnitSymbol(self) -> str:
        # Return the unit symbol based on the unit group.
        try:
            return SYMBOLS[self.unitg]
        except Exception:
            LOGGER.exception("Unit group error")
            exit()

    def __getWeatherData(self) -> Dict[Any, Any]:
        # Format the query URL and fetch weather data.
        LOGGER.info("Retrieving weather information")
        formattedQuery: str = QUERY.format(
            self.coordinates[0], self.coordinates[1], self.unitg, self.lang, API_KEY
        )
        LOGGER.debug(f"Sent query: {formattedQuery}")
        try:
            res: Response = get(formattedQuery)
            jsonData: Dict[Any, Any] = res.json()
        except exceptions.RequestException:
            LOGGER.exception("Please check your internet connection or API key.")
            exit()
        except json.JSONDecodeError:
            LOGGER.exception(
                "Response is not valid! Please check the connection and API key and try again.."
            )
            exit()
        except Exception:
            LOGGER.exception("An error occurred while retrieving weather information!")
            exit()
        else:
            return jsonData

    @staticmethod
    async def __getCoordinates() -> List[float]:
        # Get the current device's GPS coordinates.
        LOGGER.info("GPS data Retrieving")
        locator: g.Geolocator = g.Geolocator()
        try:
            pos: g.Geoposition = await locator.get_geoposition_async()
        except PermissionError:
            LOGGER.warning(
                "Permission error! Location permission could not be obtained"
            )
            exit()
        except Exception:
            LOGGER.exception("An error occurred while accessing the location!")
            exit()
        else:
            if pos.coordinate is not None:
                return [float(pos.coordinate.latitude), float(pos.coordinate.longitude)]
            else:
                LOGGER.warning("Unable to fetch coordinates.")
                exit()


def getArguments() -> List[Tuple[str, str]]:
    # Get arguments from the command line.
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
    return parser.parse_args()._get_kwargs()


def main() -> None:
    # Configuring logger
    LOGGER.setLevel(DEBUG)
    FILE_HANDLER.setLevel(WARNING)
    CONSOLE_HANDLER.setLevel(DEBUG)

    FILE_HANDLER.setFormatter(FORMATTER_FILE)
    CONSOLE_HANDLER.setFormatter(FORMATTER_CONSOLE)

    LOGGER.addHandler(FILE_HANDLER)
    LOGGER.addHandler(CONSOLE_HANDLER)

    LOGGER.debug("Data Models created")

    (csarg, lang, unitG) = getArguments()
    LOGGER.debug(
        f"getArguments() returned; coordinates: {csarg[1]} | language: {lang[1]} | unitGroup: {unitG[1]}"
    )
    # If coordinates are provided in the command line, parse them.
    if csarg[1] != "gps":
        try:
            if csarg[1].startswith("'") and csarg[1].endswith("'"):
                coordinates: List[float] = list(map(float, csarg[1][1:-1].split(",")))
                LOGGER.debug(
                    f"Coordinates to use(variable coordinates ->): {coordinates}"
                )
            else:
                raise ValueError
        except Exception:
            msg: str = f"Format of coordinates; should be 'latitude,longitude'\nUser entered: {csarg[1]}"
            LOGGER.warning(msg)
            LOGGER.exception(msg)
            exit()
    else:
        coordinates = []

    # Create Weather object and show the weather information.

    weather: Weather = Weather(coordinates, lang[1], unitG[1])
    weather.showClearText()


if __name__ == "__main__":
    main()
