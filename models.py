from typing import Dict, List, Optional

from pydantic import BaseModel


class Station(BaseModel):
    distance: Optional[int]
    latitude: Optional[float]
    longitude: Optional[float]
    useCount: Optional[int]
    id: Optional[str]
    name: Optional[str]
    quality: Optional[int]
    contribution: Optional[int | float]


class Day(BaseModel):
    datetime: Optional[str]
    datetimeEpoch: Optional[int]
    tempmax: Optional[float]
    tempmin: Optional[float]
    temp: Optional[float]
    feelslikemax: Optional[float]
    feelslikemin: Optional[float]
    feelslike: Optional[float]
    dew: Optional[float]
    humidity: Optional[float]
    precip: Optional[float]
    precipprob: Optional[int | float]
    precipcover: Optional[float]
    preciptype: Optional[List[str]]
    snow: Optional[float]
    snowdepth: Optional[float]
    windgust: Optional[float]
    windspeed: Optional[float]
    winddir: Optional[float]
    pressure: Optional[float]
    cloudcover: Optional[float]
    visibility: Optional[float]
    solarradiation: Optional[float]
    solarenergy: Optional[float]
    uvindex: Optional[int]
    severerisk: Optional[int]
    sunrise: Optional[str]
    sunriseEpoch: Optional[int]
    sunset: Optional[str]
    sunsetEpoch: Optional[int]
    moonphase: Optional[float]
    conditions: Optional[str]
    description: Optional[str]
    icon: Optional[str]
    stations: Optional[List[str]]
    source: Optional[str]


class WeatherResponse(BaseModel):
    queryCost: Optional[int]
    latitude: Optional[float]
    longitude: Optional[float]
    resolvedAddress: Optional[str]
    address: Optional[str]
    timezone: Optional[str]
    tzoffset: Optional[int]
    days: List[Day] = []
    stations: Dict[str, Station] = {}
