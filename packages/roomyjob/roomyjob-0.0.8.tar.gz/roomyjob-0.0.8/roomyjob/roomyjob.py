#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import json
import socket
import requests
import logging
logging.basicConfig()

from . import __version__ as version

HEADERS = {'Content-Type': 'application/json'}


class InvalidImageException(Exception):
    pass

def get_ipaddress():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("roomy.firebaseio.com", 443))
    return s.getsockname()[0]


def send_heartbeat(root_url, device_id=None, timeout=3):
    url = "{}/{}/last-seen.json".format(root_url, device_id)
    print "Sending heartbeat to {}".format(url)
    try:
        response = requests.patch(url, data=json.dumps({'ts': time.time(),
                                                        'ip': get_ipaddress(),
                                                        'version': version}),
                                  timeout=timeout, headers=HEADERS)
        return response
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError),\
            e:
        logging.fatal("Cannot connect to {}".format(url))
        raise e


def send_event(root_url, device_id, image_url, timeout=3):
    url = "{}/{}/events.json".format(root_url, device_id)
    logging.info("Sending event to {}".format(url))
    try:
        if not image_url.endswith('.jpg'):
            raise InvalidImageException
        response = requests.post(url, data=json.dumps({'image_url': image_url,
                                                     'timestamp': time.time()}),
                                               timeout=timeout, headers=HEADERS)
        return response
    except (InvalidImageException, requests.exceptions.Timeout,
            requests.exceptions.ConnectionError), e:
        if isinstance(e, requests.exceptions.Timeout):
            logging.fatal("Cannot connect to {}".format(url))
            raise e
        else:
            logging.fatal("Invalid image")
            raise e
