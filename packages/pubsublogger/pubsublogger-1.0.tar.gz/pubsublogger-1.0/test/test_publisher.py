#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import time
from pubsublogger import publisher

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Configure a logging publisher.')

    parser.add_argument('-s', '--use_unix_socket',  action='store_true',
            help='Use a unix socket path instead of a tcp socket.')
    parser.add_argument("--unix_socket_path", default='/tmp/redis.sock',
            type=str, help='Unix socket path.')

    parser.add_argument("-H", "--hostname", default='localhost',
            type=str, help='Set the hostname of the server.')
    parser.add_argument("-p", "--port", default=6379,
            type=int, help='Set the server port.')
    parser.add_argument("-c", "--channel",
            type=str, required=True, help='Channel to publish into.')

    args = parser.parse_args()

    if args.use_unix_socket:
        publisher.use_tcp_socket = False
        publisher.unix_socket = args.unix_socket_path
    else:
        publisher.hostname = args.hostname
        publisher.port = args.port

    publisher.channel = args.channel

    for i in range(0,21):
        if i%2 == 0 :
            publisher.info('test' + str(i))
        elif i%3 == 0 :
            publisher.warning('test' + str(i))
        elif i%5 == 0:
            publisher.error('test' + str(i))
        elif i%7 == 0:
            publisher.critical('test' + str(i))
        else:
            publisher.debug('test' + str(i))
        time.sleep(1)
