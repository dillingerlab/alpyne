import calendar
import os
from datetime import datetime
from pprint import pprint

import requests


def get_working_dataset(latitude_longitude):
    api_key = os.environ["openweather_api_key"]
    excluded_dataset = "current,minutely,hourly,alerts"
    url = "https://api.openweathermap.org"
    uri = f"{url}/data/2.5/onecall?lat={latitude_longitude}&exclude={excluded_dataset}&units=imperial&appid={api_key}"
    r = requests.get(uri)
    data = r.json()
    dataset = {}
    days = 0
    for x in data["daily"]:
        # day_weights = [{'type': 'day',
        #                'values': [2, [[-30, 40], [88, 100]], 1, [40-88]]},

        night_weights = [2, [[-30, 20], [70, 100]], 1, [20 - 70]]

        # print(type(night_weights))
        # print(night_weights)
        # print(x['feels_like']['night'])
        # print(type(x['feels_like']['night']))

        [
            print(item)
            for item in night_weights
            if x["feels_like"]["night"] not in night_weights
        ]

        # for i, x['feels_like']['night'] in enumerate(night_weights):
        #    print('night_weights(key?)' + i)

        # for i in zip(x['feels_like']):
        #    pprint[i]

        dataset[days] = {}
        dataset[days]["date"] = datetime.fromtimestamp(x["dt"])
        dataset[days]["timezone"] = data["timezone"]
        dataset[days]["day_feels_like_temp"] = x["feels_like"]["day"]
        dataset[days]["night_feels_like_temp"] = x["feels_like"]["night"]
        dataset[days]["weather"] = x["weather"][0]["description"]
        days += 1
    return dataset


def main():
    # Winona Latitude: 44.07468410 Longitude: -91.67587140
    lat_lon = "44.07468410&lon=-91.67587140"
    dataset = get_working_dataset(lat_lon)
    pprint(dataset[0])


if __name__ == "__main__":
    main()
