# Weather Application

This Python application provides users with weather information based on their geographical location. Users can retrieve weather data by providing various parameters through the command line.

## Features

- Users can get weather information either using GPS location or manually provided coordinates.
- The temperature unit can be selected as `metric`, `us`, `uk`, or `base`.
- The output language can be set to Turkish or any other selected language.
- Weather data includes the daily maximum temperature and a description.

## Usage

Install the required libraries:

`pip install -r reqirements.txt`

Run the script:

`python weather.py --coordinates latitude,longitude --language tr --unitGroup metric`
