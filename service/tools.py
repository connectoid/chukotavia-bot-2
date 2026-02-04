import datetime
import re
import requests
import random
from time import sleep
from pprint import pprint
import json

from fake_useragent import UserAgent

from database.orm import get_all_users

url = 'https://booking.chukotavia.com/websky/json/company-search-variants'
json_filename = 'tmp_db.json'

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
        result = True
    except KeyError:
        try:
            error = r.json()['error']
            if error == 'web.search.nullPricing':
                tg_message = f'Билетов на эту дату нет'
                result = False
            else:
                result = False
        except KeyError:
            print(f'Скорее всего билеты есть')
    return result, tg_message


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
    try:
        print(f'START Requesting ticets on {date} from {origin} to {destination}')
        r = requests.get(url, params=payload, headers=fake_ua)
        print(f'FINISH Requesting ticets on {date} from {origin} to {destination}')
        return parse_json(r)
    except IOError:
        print('Ошибка запроса')
    return None


def request_tickets(date, direction):
    origin = direction.split('_')[0]
    destination = direction.split('_')[1]
    result = get_ticket_info(date, origin, destination) 
    return result

    
def check_date(date):
    try:
        datetime.datetime.strptime(date,"%d.%m.%Y")
        return True
    except ValueError as err:
        print(err)
        return False
    

def convert_date(date):
    if len(date.split('.')[0]) == 1:
        date = '0' + date
    if len(date.split('.')[1]) == 1:
        date = date[:3] + '0' + date[3:]
    return date


def save_db_to_json():
    all_users = get_all_users()
    all_users_json = []
    for user in all_users:
        if user.premium and user.tickets:
            user_json = {}
            user_json['id'] = user.id
            user_json['username'] = user.username
            user_json['tg_id'] = user.tg_id
            user_json['admin'] = user.admin
            user_json['premium'] = user.premium
            user_json['everyday_message'] = user.everyday_message
            user_json['tickets'] = []
            for user_ticket in user.tickets:
                user_json['tickets'].append({'date': user_ticket.date, 'direction': user_ticket.direction})
            all_users_json.append(user_json)
    print(f'All users: {all_users_json}')
    
    all_users_json_string = json.dumps(all_users_json)
    with open(json_filename, 'w') as json_file:
        json_file.write(all_users_json_string)
    return all_users_json


def load_dict_from_json():
    with open(json_filename, 'r') as json_file:
        all_users_json_string = json_file.read()
        all_users_json = json.loads(all_users_json_string)
    return all_users_json