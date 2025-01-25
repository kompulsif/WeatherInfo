# Weather Application

This Python application provides users with weather information based on their geographical location. Users can retrieve weather data by providing various parameters through the command line.

## Features

- Users can get weather information either using GPS location, IP location or manually provided coordinates.
* --coordinates parameter can take them; `gps`, `ip`, `c:latitude,longitude`
- The temperature unit can be selected as `metric`, `us`, `uk`, or `base`.
- The output language can be set to Turkish or any other selected language.
- Weather data includes the daily maximum temperature and a description.

## Usage

First of all, the .env file needs to be created, for this, a copy of the .env.example file must be created and the necessary fields must be filled in.

`cp .env.example .env`

Install the required libraries:

`pip install -r reqirements.txt`

Firstly, run the Redis Server(Ubuntu WSL was used):

`sudo systemctl start redis`

Run the Celery Worker. Run in terminal:

`celery -A weather worker --loglevel=info --pool=solo`

Then run the weather.py :

`python weather.py --coordinates 'c:latitude,longitude' --language tr --unitGroup metric`

Ex:
`python weather.py --coordinates c:39.927200,32.864400 --language tr --unitGroup metric`
