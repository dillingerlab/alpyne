import calendar
import os
from datetime import datetime
from pprint import pprint

import requests


def get_working_dataset(latitude_longitude):
    api_key = os.environ['openweather_api_key']
    excluded_dataset = 'current,minutely,hourly,alerts'
    url = 'https://api.openweathermap.org'
    uri = f'{url}/data/2.5/onecall?lat={latitude_longitude}&exclude={excluded_dataset}&units=imperial&appid={api_key}'
    r = requests.get(uri)
    data = r.json()
    dataset = {}
    days = 0
    for x in data['daily']:
        dataset[days] = {}
        dataset[days]['date'] = datetime.fromtimestamp(x['dt'])
        dataset[days]['timezone'] = data['timezone']
        dataset[days]['day_fl_temp'] = x['feels_like']['day']
        dataset[days]['night_fl_temp'] = x['feels_like']['night']
        dataset[days]['weather'] = x['weather'][0]['description']
        days += 1
    return dataset


def main():
    # Winona Latitude: 44.07468410 Longitude: -91.67587140
    lat_lon = '44.07468410&lon=-91.67587140'
    dataset = get_working_dataset(lat_lon)
    print(dataset)


if __name__ == '__main__':
    main()
