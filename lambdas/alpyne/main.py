#!./.venv/bin/python3
import json
import logging
import os
from datetime import datetime
from textwrap import dedent
from xmlrpc.client import boolean

import boto3
import requests
import yaml
from twilio.rest import Client

logging.basicConfig(level=logging.INFO)


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
    except KeyError:
        api_key = get_secret(secret_container="openweather", region_name="us-east-1", secret_key="api_secret")
        logging.debug("Using secretsmanager")

    excluded_dataset = "current,minutely,hourly,alerts"
    url = "https://api.openweathermap.org"
    uri = f"data/2.5/onecall?lat={latitude}&lon={longitude}&exclude={excluded_dataset}&units=imperial&appid={api_key}"
    api_endpoint = f"{url}/{uri}"
    r = requests.get(api_endpoint)
    return r.json()


def get_weekend_status(crag: str, data: dict) -> dict:
    """
    Updates OpenWeather Dataset as needed
    """


def get_forecast() -> list:
    """
    Create sms messge with next 3 dyas of weather for known crags
    """

    with open("cords.yml", "r") as f:
        doc = yaml.load(f, Loader=yaml.FullLoader)

    keys = []
    for x in doc:
        keys.append(x)

    dataset = {}

    for crag in keys:
        latitude = doc[crag]["latitude"]
        longitude = doc[crag]["longitude"]

        raw_data = get_working_dataset(latitude, longitude)
        dataset[crag] = {}
        for x in raw_data["daily"]:
            day_of_the_week = datetime.fromtimestamp(x["dt"]).strftime("%A")
            dataset[crag][day_of_the_week] = {"weather": x["weather"][0]["description"], "high": x["temp"]["max"]}

    return dataset


def create_sms_message(dataset: dict) -> str:
    location_string = ""
    for crag, days in dataset.items():
        gather = ""
        for day, data_point in days.items():
            weather = data_point["weather"]
            high = data_point["high"]
            temp_string = dedent(
                f"""{day}
{weather}:{high}
            """
            )
            gather = gather + temp_string

        location_string = dedent(
            f"""
{location_string}
{crag}
{gather}
        """
        )
    return location_string


def send_sms_message(message: list) -> boolean:
    try:
        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        logging.debug("Using OS Env Var")
    except KeyError:
        account_sid = get_secret(secret_container="twilio", region_name="us-east-1", secret_key="account_sid")
        logging.debug("using secretsmanager")

    try:
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        logging.debug("Using OS Env Var")
    except KeyError:
        auth_token = get_secret(secret_container="twilio", region_name="us-east-1", secret_key="auth_token")
        logging.debug("using secretsmanager")

    try:
        from_number = os.environ["TWILIO_FROM_NUMBER"]
        logging.debug("Using OS Env Var")
    except KeyError:
        from_number = get_secret(secret_container="twilio", region_name="us-east-1", secret_key="from_number")
        logging.debug("using secretsmanager")

    try:
        to_number = os.environ["TWILIO_TO_NUMBER"]
        logging.debug("Using OS Env Var")
    except KeyError:
        to_number = get_secret(secret_container="twilio", region_name="us-east-1", secret_key="to_number")
        logging.debug("using secretsmanager")

    client = Client(account_sid, auth_token)

    client.api.account.messages.create(to=to_number, from_=from_number, body=str(message))

    return True


def handler(event, context):
    dataset = get_forecast()
    message = create_sms_message(dataset)
    logging.debug(message)

    status = send_sms_message(message)

    return status


if __name__ == "__main__":
    forecast_dataset = get_forecast()
    logging.debug(forecast_dataset)
    sms_message = create_sms_message(forecast_dataset)
    logging.debug(sms_message)
    status = send_sms_message(sms_message)
