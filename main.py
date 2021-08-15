import calendar
import os
from datetime import datetime
from pprint import pprint

import requests


def main():
    """Description of the function"""
    api_key = os.environ['openweather_api_key']
    # Winona Latitude: 44.07468410 Longitude: -91.67587140
    lat_lon = '44.07468410&lon=-91.67587140'
    excluded_dataset = 'current,minutely,hourly,alerts '
    url = 'https://api.openweathermap.org'
    uri = f'{url}/data/2.5/onecall?lat={lat_lon}&exclude={excluded_dataset}&units=imperial&appid={api_key}'
    r = requests.get(uri)
    data = r.json()
    timezone = data['timezone']
    for x in data['daily']:
        date = datetime.fromtimestamp(x['dt'])
        pprint('date: ' + str(date) + ' ' + timezone + ' which is a ' + calendar.day_name[date.weekday()])
        pprint('feels like: ' + str(x['feels_like']))
        pprint('temps: ' + str(x['temp']))
        pprint('rain: ' + str(x.get('rain')))
        pprint('humidity: ' + str(x['humidity']))


if __name__ == '__main__':
    main()
