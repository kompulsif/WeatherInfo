from typing import Dict, List, Optional

from pydantic import BaseModel


class Station(BaseModel):
    distance: int
    latitude: float
    longitude: float
    useCount: int
    id: str
    name: str
    quality: int
    contribution: int


class Day(BaseModel):
    datetime: str
    datetimeEpoch: int
    tempmax: float
    tempmin: float
    temp: float
    feelslikemax: float
    feelslikemin: float
    feelslike: float
    dew: float
    humidity: float
    precip: Optional[float]
    precipprob: Optional[int | float]
    precipcover: float
    preciptype: Optional[List[str]]
    snow: Optional[float]
    snowdepth: Optional[float]
    windgust: float
    windspeed: float
    winddir: float
    pressure: float
    cloudcover: float
    visibility: float
    solarradiation: float
    solarenergy: float
    uvindex: int
    severerisk: int
    sunrise: Optional[str]
    sunriseEpoch: Optional[int]
    sunset: Optional[str]
    sunsetEpoch: Optional[int]
    moonphase: float
    conditions: str
    description: str
    icon: str
    stations: List[str]
    source: str


class WeatherResponse(BaseModel):
    queryCost: int
    latitude: float
    longitude: float
    resolvedAddress: str
    address: str
    timezone: str
    tzoffset: int
    days: List[Day] = []
    stations: Dict[str, Station] = {}
