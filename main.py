#!./.venv/bin/python3

import os
from datetime import datetime
from pprint import pprint

import requests
import yaml


def calc_rating(temp_max, temp_low, day_feel_like, night_feel_like):
    rating = 0
    high = {-1: list(range(-30, 40)),
            -2: list(range(40, 60)),
            3: list(range(60, 80)),
            2: list(range(80, 90)),
            1: list(range(90, 130))}
    for ranger in high:
        if temp_max in high[ranger]:
            rating = ranger
    return rating


def get_working_dataset(latitude, longitude):
    api_key = os.environ["openweather_api_key"]
    excluded_dataset = "current,minutely,hourly,alerts"
    url = "https://api.openweathermap.org"
    uri = f"data/2.5/onecall?lat={latitude}&lon={longitude}&exclude={excluded_dataset}&units=imperial&appid={api_key}"
    api_endpoint = f"{url}/{uri}"
    r = requests.get(api_endpoint)
    data = r.json()
    dataset = {}
    days = 0
    for x in data["daily"]:
        # pprint(x)
        dataset[days] = {}
        dataset[days]["date"] = datetime.fromtimestamp(x["dt"]).strftime("%m/%d")
        dataset[days]["day_of_the_week"] = datetime.fromtimestamp(x["dt"]).strftime(
            "%A"
        )
        dataset[days]["day_feels_like_temp"] = x["feels_like"]["day"]
        dataset[days]["temp_max"] = x["temp"]["max"]
        dataset[days]["night_feels_like_temp"] = x["feels_like"]["night"]
        dataset[days]["weather"] = x["weather"][0]["description"]

        dataset[days]["rating"] = calc_rating(1, 2, 3, 4)

        days += 1
    return dataset


def main():
    # Winona Latitude: 44.07468410 Longitude: -91.67587140
    with open("cords.yml", "r") as f:
        doc = yaml.load(f, Loader=yaml.FullLoader)
    keys = []
    for x in doc:
        keys.append(x)

    for i in keys:
        latitude = doc[i]["latitude"]
        longitude = doc[i]["longitude"]

        dataset = get_working_dataset(latitude, longitude)
        print(f'Dataset: {dataset}')

    with open('rating_schema.yml', 'r') as f:
        ratings = yaml.load(f, Loader=yaml.FullLoader)
    pprint(ratings)
    pprint(ratings['Day Time Feel Like'])

    print(f"Crag: {i}")
    #for day in dataset:
    #    pprint(dataset[day])
    pprint(calc_rating(76.5, 2, 3, 4))
    # Call Twilio


if __name__ == "__main__":
    main()
