#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Usage:
    roomyjob heartbeat --device <DEVICE_ID> [--timeout=<SECONDS>]
    roomyjob event --device <DEVICE_ID> --url <URL> [--timeout=<SECONDS>]

Options:
  -h --help                         Show this help message and exit
  --version                         Show version and exit
  -d --device=DEVICE_ID             Device ID of the device the job is running
                                    on
  -r --service-root=SERVICE_ROOT    Root URL to post data to
                                    [default: https://roomy.firebaseio.com/]
  -n --name                         Device Name
  -i --ip                           Device IP Address
  -u --url=URL                      URL of the uploaded image
  -t --timeout=SECONDS              Connection timeout
                                    [default: 3]
  --debug=DEBUG                     [default: True]
"""

__author__ = 'Ben Hughes'
__email__ = 'bwghughes@gmail.com'
__version__ = '0.0.6'

from roomyjob import send_heartbeat, send_event, InvalidImageException

__all__ = ['send_heartbeat', 'send_event', 'InvalidImageException']
ROOT_DEVICE_URL = "https://roomy.firebaseio.com/device"


def dispatch(arguments):
    if arguments.get('heartbeat'):
        print send_heartbeat(ROOT_DEVICE_URL, arguments.get('--device'),
                             float(arguments.get('--timeout')))
    elif arguments.get('event'):
        print send_event(ROOT_DEVICE_URL, arguments.get('--device'),
                         arguments.get('--url'),
                         float(arguments.get('--timeout')))


def main():
    from docopt import docopt
    dispatch(docopt(__doc__, version=__version__))


if __name__ == '__main__':
    main()
