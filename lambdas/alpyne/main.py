#!./.venv/bin/python3
import json
import logging
import os
from datetime import datetime
from textwrap import dedent

import boto3
import requests
import yaml

logging.basicConfig(level=logging.INFO)


def calc_rating(category: str, temperature: float):
    with open("rating_schema.yml", "r") as f:
        ratings = yaml.load(f, Loader=yaml.FullLoader)
    rating = 0

    for key in ratings[category].keys():
        if int(temperature) in list(range(ratings[category][key][0], ratings[category][key][1])):
            rating = key
    return rating


def get_secret(secret_container: str, region_name: str, secret_key: str) -> str:
    """
    connect and access SecretsManager secret
    """
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    get_secret_value_response = client.get_secret_value(SecretId=secret_container)
    secrets = json.loads(get_secret_value_response["SecretString"], strict=False)
    return secrets[secret_key]


def get_working_dataset(latitude: float, longitude: float) -> dict:
    """
    Connect to SecretsManager and get API secret for OpenWeather,
    then get and return weather data for lat/lon

    TODO: Function is do this and this and this, should be purposeful
    """
    try:
        api_key = os.environ["openweather_api_key"]
        logging.debug("Using OS Env Var")
    except KeyError as e:
        api_key = get_secret(secret_container="openweather", region_name="us-east-1", secret_key="api_secret")
        logging.debug("using secretsmanager")
    except:
        raise e

    excluded_dataset = "current,minutely,hourly,alerts"
    url = "https://api.openweathermap.org"
    uri = f"data/2.5/onecall?lat={latitude}&lon={longitude}&exclude={excluded_dataset}&units=imperial&appid={api_key}"
    api_endpoint = f"{url}/{uri}"
    r = requests.get(api_endpoint)
    return r.json()


def update_weather_data(data: dict) -> dict:
    """
    Updates OpenWeather Dataset as needed
    """
    dataset = {}
    days = 0
    for x in data["daily"]:
        # pprint(x)
        dataset[days] = {}
        dataset[days]["date"] = datetime.fromtimestamp(x["dt"]).strftime("%m/%d")
        dataset[days]["day_of_the_week"] = datetime.fromtimestamp(x["dt"]).strftime("%A")
        dataset[days]["day_feels_like_temp"] = x["feels_like"]["day"]
        dataset[days]["feel_like_rating"] = calc_rating("Day Time Feel Like", dataset[days]["day_feels_like_temp"])
        dataset[days]["high"] = x["temp"]["max"]
        dataset[days]["high_rating"] = calc_rating("high", dataset[days]["day_feels_like_temp"])
        dataset[days]["night_feels_like_temp"] = x["feels_like"]["night"]
        dataset[days]["weather"] = x["weather"][0]["description"]

        days += 1
    return dataset


def get_weekend_status(data: dict) -> dict:
    """
    Updates OpenWeather Dataset as needed
    """
    dataset = {}
    days = 0
    for x in data["daily"]:
        # pprint(x)
        dataset[days] = {}
        dataset[days]["date"] = datetime.fromtimestamp(x["dt"]).strftime("%m/%d")
        dataset[days]["day_of_the_week"] = datetime.fromtimestamp(x["dt"]).strftime("%A")
        dataset[days]["high"] = x["temp"]["max"]
        dataset[days]["weather"] = x["weather"][0]["description"]

        days += 1
    return dataset


def weekend_forecast() -> list:
    """
    Create sms messge with next 3 dyas of weather for known crags
    """

    output = []

    with open("cords.yml", "r") as f:
        doc = yaml.load(f, Loader=yaml.FullLoader)

    keys = []
    for x in doc:
        keys.append(x)

    for i in keys:
        latitude = doc[i]["latitude"]
        longitude = doc[i]["longitude"]

        raw_data = get_working_dataset(latitude, longitude)
        dataset = get_weekend_status(raw_data)

        location_string = dedent(
            f"""
            Crag: {i}
            Day: {dataset[0]['day_of_the_week']}, {dataset[0]['weather']}, {dataset[0]['high']}
            Day: {dataset[1]['day_of_the_week']}, {dataset[1]['weather']}, {dataset[1]['high']}
            Day: {dataset[2]['day_of_the_week']}, {dataset[2]['weather']}, {dataset[2]['high']}
            """
        )
        output.append(location_string)
    return output


def handler(event, context):
    return weekend_forecast()

    # secretManagerClient(<region>)
    # GetSecretValueCommand(<secretid>)
    # response = clitn)
    # parse


if __name__ == "__main__":
    forecast = weekend_forecast()
    for x in forecast:
        print(x)
