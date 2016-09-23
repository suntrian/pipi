#coding: utf-8

import socket
import time

host = ''
port = 12012

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind((host, port))

while True:
    try:
        data, addr = s.recvfrom(1024)
        print('get %s from %s'%(data, addr))
    except KeyboardInterrupt:
        pass
    finally:
        time.sleep(10)

