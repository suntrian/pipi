#!/usr/python3.5

# encoding:utf-8

'''
    心知天气api
    doc_url:http://www.thinkpage.cn/doc#sign

    新浪天气api
    api：http://php.weather.sina.com.cn/iframe/index/w_cl.php?code=js&day=0&city=&dfc=1&charset=utf-8

'''


import time
import hashlib
import hmac
import base64
import requests
import json

api = 'https://api.thinkpage.cn/v3/weather/now.json?'
location = 'beijing'
uid = 'U20E304E3C'
key = 'os08tnjdsqvbpzir'
language = 'en'
unit = 'c'


def get_sha_url(ttl=60):
    ts = int(time.time())
    pa_str = b'ts=%d&ttl=%d&uid=%b' % (ts, ttl, uid)
    pa = hmac.new(key, pa_str, hashlib.sha1).hexdigest()
    pa = base64.b64encode(bytes(pa, encoding='utf-8'))
    ba64_pa = base64.b64encode(pa)
    url = api + pa_str.decode(encoding='utf-8') + 'sig=%s' % ba64_pa.decode(
        encoding='utf-8') + '&location=%s&language=%s&unit=%s' % (location, language, unit)
    return url


def get_nomal_url():
    return '%skey=%s&location=%s&language=%s&unit=%s' % (api, key, location, language, unit)


def get_weather(url):
    data = requests.get(url).json()
    return data

if __name__ == "__main__":
    print(str(get_weather(get_nomal_url())))
