import asyncio
import os
from argparse import ArgumentParser
from logging import DEBUG, WARNING, Formatter, Logger, StreamHandler
from logging.handlers import RotatingFileHandler
from platform import system
from typing import Any, Dict, List, Tuple

from celery import Celery
from dotenv import load_dotenv
from requests import Response, exceptions, get

from models import *

if (system() == "Windows"):
    import winsdk.windows.devices.geolocation as g
    
load_dotenv()

WEATHER_API_KEY: str = os.environ["WEATHER_API_KEY"]
GEO_API_KEY: str = os.environ["GEO_API_KEY"]
QUERY_WEATHER: str = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{},{}/today?unitGroup={}&lang={}&key={}&contentType=json&include=days"
QUERY_GEOIP: str = "https://ipinfo.io/json?token={}"
SYMBOLS: Dict[str, str] = {"metric": "°C", "us": "°F", "uk": "°C", "base": "K"}
BROKER: str = os.environ["REDIS_BROKER"].rstrip("/")
BACKEND: str = os.environ["REDIS_BACKEND"].rstrip("/")
PORT: str = os.environ["REDIS_PORT"]
DB: str = os.environ["REDIS_DB"]

weatherApp = Celery(
    "weather",
    broker=f"{BROKER}:{PORT}/{DB}",
    backend=f"{BACKEND}:{PORT}/{DB}",
)

logger = Logger(__name__)
formatter_console = Formatter("%(levelname)s - %(message)s")
formatter_file = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler = RotatingFileHandler(filename="process_log.log", mode="a", maxBytes=50000)
console_handler = StreamHandler()


class Weather:
    def __init__(
        self,
        coordinates: List[float] | str = [],
        lang: str = "tr",
        unitg: str = "metric",
    ) -> None:
        # If no coordinates are provided, get the coordinates using GPS.

        if coordinates == "gps":
            cs: List[float] = asyncio.run(Weather.__getCoordinatesByGPS())
        elif coordinates == "ip":
            cs: List[float] = asyncio.run(Weather.__getCoordinatesByIP())
        else:
            cs: List[float] = coordinates

        logger.debug(f"Coordinates to use(variable -> cs): {cs}")
        self.coordinates: List[float] = cs
        self.lang: str = lang
        self.unitg: str = unitg
        self.symbol: str = self.getUnitSymbol()

    def getUnitSymbol(self) -> str:
        # Return the unit symbol based on the unit group.
        try:
            return SYMBOLS[self.unitg]
        except Exception:
            logger.exception("Unit group error")
            exit()

    async def showClearText(self) -> str:
        # Get weather data and print the maximum temperature and description.
        data: Dict[Any, Any] = await self.__getWeatherData()
        logger.info("Weather data received")
        try:
            weatherReponse = WeatherResponse(**data)
            temp: float = weatherReponse.days[0].tempmax
            description: str = weatherReponse.days[0].description

            return f"\n\n{self.coordinates[0]},{self.coordinates[1]} | {temp}{self.symbol} -> {description}\n\n"
        except Exception as msg:
            logger.critical(msg)
        return ""

    async def __getWeatherData(self) -> Dict[Any, Any]:
        # Format the query URL and fetch weather data.
        logger.info("Retrieving weather information")
        formattedQuery: str = QUERY_WEATHER.format(
            self.coordinates[0],
            self.coordinates[1],
            self.unitg,
            self.lang,
            WEATHER_API_KEY,
        )
        logger.debug(f"Sent query: {formattedQuery}")
        try:
            res: Response = get(formattedQuery)
            jsonData: Dict[Any, Any] = res.json()
        except exceptions.RequestException:
            logger.exception("Please check your internet connection or API key.")
            exit()
        except Exception:
            logger.exception("An error occurred while retrieving weather information!")
            exit()
        else:
            return jsonData

    @staticmethod
    async def __getCoordinatesByGPS() -> List[float]:
        # Get the current device's GPS coordinates asynchronously.
        logger.info("GPS data Retrieving")
        locator: g.Geolocator = g.Geolocator()
        try:
            pos: g.Geoposition = await locator.get_geoposition_async()
        except PermissionError:
            logger.warning(
                "Permission error! Location permission could not be obtained"
            )
            exit()
        except Exception:
            logger.exception("An error occurred while accessing the location!")
            exit()
        else:
            if pos.coordinate is not None:
                return [float(pos.coordinate.latitude), float(pos.coordinate.longitude)]
            else:
                logger.critical("Unable to fetch coordinates by gps")
                exit()

    @staticmethod
    async def __getCoordinatesByIP() -> List[float]:
        try:
            formattedQuery: str = QUERY_GEOIP.format(GEO_API_KEY)
            r: Response = get(formattedQuery)
            jsonData: Dict[str, str] = r.json()
        except Exception as ex:
            logger.critical(
                f"An error occurrred while getting the location by ip!\nDescription: {ex}"
            )
            exit()
        else:
            if jsonData:
                loc: str = jsonData.get("loc", "")
                if loc:
                    return [float(i) for i in loc.split(",")]
                else:
                    logger.critical("Unable to fetch coordinates by ip")
                    exit()
            else:
                logger.critical("Unable to fetch coordinates by ip")
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


@weatherApp.task(bind=True)
def weatherRequestResults(
    self, coordinates: List[float] | str, lang: str, unitg: str
) -> str:
    # Create Weather object and show the weather information.
    weather = Weather(coordinates, lang, unitg)

    result = asyncio.run(weather.showClearText())
    return result


def main() -> None:
    # Configuring logger
    logger.setLevel(DEBUG)
    file_handler.setLevel(WARNING)
    console_handler.setLevel(DEBUG)

    file_handler.setFormatter(formatter_file)
    console_handler.setFormatter(formatter_console)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.debug("Data Models created")

    (csarg, lang, unitG) = getArguments()
    logger.debug(
        f"getArguments() returned; coordinates: {csarg[1]} | language: {lang[1]} | unitGroup: {unitG[1]}"
    )
    # If coordinates are provided in the command line, parse them.
    coordinates: List[float] | str = ""
    if csarg[1] != "gps" and csarg[1] != "ip":
        try:
            if csarg[1].startswith("c:"):
                coordinates = list(map(float, csarg[1][2:].replace(" ", "").split(",")))
                logger.debug(
                    f"Coordinates to use(variable coordinates ->): {coordinates}"
                )
            else:
                raise ValueError
        except Exception:
            msg: str = f"Format of coordinates; should be 'latitude,longitude'\nUser entered: {csarg[1]}"
            logger.warning(msg)
            logger.exception(msg)
            return
    else:
        coordinates = csarg[1]

    try:
        results = weatherRequestResults.delay(coordinates, lang[1], unitG[1])
        print(results.get(timeout=5))
    except Exception as msg:
        logger.critical(msg)
        logger.exception(msg)


if __name__ == "__main__":
    main()
