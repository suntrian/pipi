#!/usr/python3.5

# encoding:utf-8

import time
import requests
import json

'''
    Data：nowapi
    URL: https://www.nowapi.com/
    apk sample:http://api.k780.com:88/?app=finance.shgold&appkey=10003&sign=b59bc3ef6191eb9f747dd4e83c99f2a4&format=json
'''

appkey = '21096'
secret = '91e0a8b1532620da6a1a3c023039d7f9'
sign = '186e6271a194c3c5a65ee463b210cdac'

api = 'http://api.k780.com:88/?app=finance.shgold&appkey=%s&sign=%s&format=json' % (appkey, sign)


def get_data(url):
    data = requests.get(api).json()
    return data


if __name__ == '__main__':
    print(get_data(api))
