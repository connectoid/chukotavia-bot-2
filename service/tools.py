import datetime
import re
import requests
import random
from time import sleep

from fake_useragent import UserAgent

url = 'https://booking.chukotavia.com/websky/json/company-search-variants'

# Provideniya - PVS
# Anadyr - DYR

ua = UserAgent()
fake_ua = {'user-agent': ua.random}


def parse_json(r):
    tg_message = f'Билетов на эту дату нет'
    try:
        origincityName = r.json()['flights'][0]['flights'][0]['origincityName']
        destinationcityName = r.json()['flights'][0]['flights'][0]['destinationcityName']
        departuredate = r.json()['flights'][0]['flights'][0]['departuredate']
        originalPrice = r.json()['prices'][0]['originalPrice']
        available = r.json()['prices'][0]['flight_variants'][0]['direction'][0]['available']
        tg_message = f'{datetime.date.today()}: Есть билеты на {departuredate} по маршруту {origincityName} - {destinationcityName} по цене {originalPrice} руб. в количестве {available} шт.'
        # send_message(tg_message)
    except KeyError:
        print(f'Скорее всего билетов нет')
        try:
            error = r.json()['error']
            if error == 'web.search.nullPricing':
                tg_message = f'Билетов на эту дату нет'
        except KeyError:
            print(f'Скорее всего билеты есть')
    return tg_message


def get_ticket_info(date, origin, destination):
    payload = {
        'searchGroupId': 'standard',
        'segmentsCount': '1',
        'date[0]': date,
        'origin-city-code[0]': origin,
        'destination-city-code[0]': destination,
        #'destination-port-code[0]': destination,
        'adultsCount': '1',
        'childrenCount': '0',
        'infantsWithSeatCount': '0',
        'infantsWithoutSeatCount': '0',
    }
    print(payload)
    try:
        r = requests.get(url, params=payload, headers=fake_ua)
        return parse_json(r)
    except IOError:
        print('Ошибка запроса')
    return None


def request_tickets(date, direction):
    origin = direction.split('_')[0]
    destination = direction.split('_')[1]
    result = get_ticket_info(date, origin, destination)
    return result

    
def check_and_convert_date(date):
    try:
        datetime.datetime.strptime(date,"%d.%m.%Y")
        return True
    except ValueError as err:
        print(err)
        return False
    
