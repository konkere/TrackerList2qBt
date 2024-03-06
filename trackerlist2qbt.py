#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Python 3.10

import re
from qbittorrentapi import Client
from argparse import ArgumentParser
from urllib.request import Request, urlopen


def args_parser():
    parser = ArgumentParser(description='TrackerList to qBittorrent')
    parser.add_argument('-u', '--url', type=str, help='URL to list of trackers.', required=False)
    parser.add_argument('-q', '--qbthost', type=str, help='URL to host with qBittorrent instance.',
                        required=True)
    parser.add_argument('-l', '--login', type=str, help='Login/user (qBittorrent)', required=True)
    parser.add_argument('-p', '--pass', type=str, help='Password (qBittorrent)', required=True)
    arguments = parser.parse_args().__dict__
    return arguments


def generate_client(host, username, password):
    client = Client(
        host=host,
        username=username,
        password=password,
        VERIFY_WEBUI_CERTIFICATE=False,
    )
    return client


def tracker_list(url):
    trackers = []
    pattern = r'^((https?|udp)://[A-z0-9\.\:\/-]*)$'
    headers = {'User-Agent': 'Mozilla/5.0'}
    data = urlopen(Request(url, headers=headers))
    content = data.read().decode(data.headers.get_content_charset('UTF-8'))
    lines = content.split('\n')
    for line in lines:
        try:
            tracker = re.match(pattern, line).group(1)
        except AttributeError:
            continue
        else:
            trackers.append(tracker)
    return trackers


def main():
    args = args_parser()
    args['url'] = 'https://cf.trackerslist.com/best.txt' if not args['url'] else args['url']
    client = generate_client(args['qbthost'], args['login'], args['pass'])
    fresh_trackers = tracker_list(args['url'])
    current_trackers = client.app.preferences.get('add_trackers').split('\n')
    difference = list(set(fresh_trackers).symmetric_difference(set(current_trackers)))
    match len(difference) > 0, len(fresh_trackers) > 0:
        case True, True:
            trackers = '\n'.join(fresh_trackers)
            client.app.setPreferences({'add_trackers': trackers})


if __name__ == '__main__':
    main()
