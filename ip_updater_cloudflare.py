#!/usr/bin/env python3

import datetime
import json
import os
import requests
import sys
import syslog


CONFIGURATION_DIRECTORY = '/etc/ip_updater'
CONFIGURATION_FILE = CONFIGURATION_DIRECTORY + '/ip_updater.conf'
HOSTS_FILE = CONFIGURATION_DIRECTORY + '/hosts_c.data'

TELEGRAM_TOKEN = None
TELEGRAM_CHAT_ID = None


def main():
    global TELEGRAM_TOKEN
    global TELEGRAM_CHAT_ID

    if not os.path.isdir(CONFIGURATION_DIRECTORY):
        write_to_syslog(syslog.LOG_ERR, 'Cannot find configuration directory', telegram_message=False)
        sys.exit(-1)

    if not os.path.isfile(CONFIGURATION_FILE):
        write_to_syslog(syslog.LOG_ERR, 'Cannot find configuration file', telegram_message=False)
        sys.exit(-1)

    if not os.path.isfile(HOSTS_FILE):
        write_to_syslog(syslog.LOG_ERR, 'Cannot find hosts file', telegram_message=False)
        sys.exit(-1)

    with open(CONFIGURATION_FILE, 'r') as configuration_file:
        try:
            configuration = json.load(configuration_file)

            if 'telegram_token' in configuration:
                TELEGRAM_TOKEN = configuration['telegram_token']

            if 'telegram_chat_id' in configuration:
                TELEGRAM_CHAT_ID = configuration['telegram_chat_id']

        except json.JSONDecodeError:
            write_to_syslog(syslog.LOG_ERR, 'Cannot parse configuration file', telegram_message=False)
            sys.exit(-1)

    public_ip = get_server_public_ip()

    if public_ip is None:
        sys.exit(-1)

    with (open(HOSTS_FILE, 'r') as hosts_file):
        try:
            hosts = json.load(hosts_file)

            for host in hosts:
                if ('always_update' not in host
                        or 'host_name' not in host
                        or 'updater' not in host
                        or 'zone_id' not in host
                        or 'dns_record_id' not in host
                        or 'bearer' not in host):
                    warning_message = f'Invalid host configuration:{os.linesep * 2}{json.dumps(host, indent=4)}'
                    write_to_syslog(syslog.LOG_WARNING, warning_message)
                    continue

                host_name = host['host_name']
                host_ip = get_host_ip(host_name,
                                      host['updater'],
                                      host['zone_id'],
                                      host['dns_record_id'],
                                      host['bearer'])

                if host_ip is None:
                    continue

                if host['always_update'] or host_ip != public_ip:
                    update_host_ip(host['host_name'],
                                   host['updater'],
                                   host['zone_id'],
                                   host['dns_record_id'],
                                   host['bearer'],
                                   public_ip)
                else:
                    info_message = f'Host {host_name} IP is already up to date'
                    write_to_syslog(syslog.LOG_INFO, info_message, disable_telegram_notification=True)

        except json.JSONDecodeError:
            write_to_syslog(syslog.LOG_ERR, 'Cannot parse hosts file', telegram_message=True)
            sys.exit(-1)


def get_host_ip(host_name, updater, zone_id, dns_record_id, bearer):
    updater = updater.replace('<ZONE_ID>', zone_id).replace('<DNS_RECORD_ID>', dns_record_id)

    try:
        response = requests.get(updater, headers={'Authorization': f'Bearer {bearer}'})
    except requests.exceptions.ConnectionError:
        error_message = f'Cannot connect to Cloudflare:{os.linesep * 2}{updater}'
        write_to_syslog(syslog.LOG_ERR, error_message)
        return None
    except requests.exceptions.Timeout:
        error_message = f'Timeout connecting to Cloudflare:{os.linesep * 2}{updater}'
        write_to_syslog(syslog.LOG_ERR, error_message)
        return None
    except requests.exceptions.TooManyRedirects:
        error_message = f'Too many redirects connecting to Cloudflare:{os.linesep * 2}{updater}'
        write_to_syslog(syslog.LOG_ERR, error_message)
        return None

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        error_message = f'Error getting the IP from Cloudflare:{os.linesep * 2}{response.text}'
        write_to_syslog(syslog.LOG_ERR, error_message)
        return None

    response = response.json()

    if response['success'] and response['result']['name'] == host_name:
        return response['result']['content']
    else:
        error_message = f'Error getting the IP from Cloudflare:{os.linesep * 2}{json.dumps(response, indent=4)}'
        write_to_syslog(syslog.LOG_ERR, error_message)
        return None


def get_server_public_ip():
    try:
        response = requests.get('https://ipinfo.io/json')
    except requests.exceptions.ConnectionError:
        write_to_syslog(syslog.LOG_ERR, 'Cannot connect to ipinfo.io')
        return None
    except requests.exceptions.Timeout:
        write_to_syslog(syslog.LOG_ERR, 'Timeout connecting to ipinfo.io')
        return None
    except requests.exceptions.TooManyRedirects:
        write_to_syslog(syslog.LOG_ERR, 'Too many redirects connecting to ipinfo.io')
        return None

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        error_message = f'Error getting the IP from ipinfo.io:{os.linesep * 2}{response.text}'
        write_to_syslog(syslog.LOG_ERR, error_message)
        return None

    response = response.json()

    if 'ip' not in response:
        error_message = f'No IP in the response from ipinfo.io:{os.linesep * 2}{json.dumps(response, indent=4)}'
        write_to_syslog(syslog.LOG_ERR, error_message)
        return None

    return response['ip']


def send_telegram_message(message, disable_notification=False):
    if TELEGRAM_TOKEN is None or TELEGRAM_CHAT_ID is None:
        write_to_syslog(syslog.LOG_WARNING, 'Telegram configuration is missing', telegram_message=False)
        return

    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    request_body = {
        'chat_id': TELEGRAM_CHAT_ID,
        'disable_notification': disable_notification,
        'text': f'{current_datetime}{os.linesep * 2}{message}'
    }

    try:
        response = requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage', json=request_body)
    except requests.exceptions.ConnectionError:
        write_to_syslog(syslog.LOG_ERR, 'Cannot connect to telegram.org', telegram_message=False)
        return
    except requests.exceptions.Timeout:
        write_to_syslog(syslog.LOG_ERR, 'Timeout connecting to telegram.org', telegram_message=False)
        return
    except requests.exceptions.TooManyRedirects:
        write_to_syslog(syslog.LOG_ERR, 'Too many redirects connecting to telegram.org', telegram_message=False)
        return

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        error_message = f'Cannot send message to Telegram:{os.linesep * 2}{response.text}'
        write_to_syslog(syslog.LOG_ERR, error_message, telegram_message=False)
        return


def update_host_ip(host_name, updater, zone_id, dns_record_id, bearer, public_ip):
    updater = updater.replace('<ZONE_ID>', zone_id).replace('<DNS_RECORD_ID>', dns_record_id)

    request_body = {
        'content': public_ip,
        'name': host_name,
        'type': 'A'
    }

    try:
        response = requests.patch(updater, json=request_body, headers={'Authorization': f'Bearer {bearer}'})
    except requests.exceptions.ConnectionError:
        error_message = f'Cannot connect to the updater service:{os.linesep * 2}{updater}'
        write_to_syslog(syslog.LOG_ERR, error_message)
        return
    except requests.exceptions.Timeout:
        error_message = f'Timeout connecting to the updater service:{os.linesep * 2}{updater}'
        write_to_syslog(syslog.LOG_ERR, error_message)
        return
    except requests.exceptions.TooManyRedirects:
        error_message = f'Too many redirects connecting to the updater service:{os.linesep * 2}{updater}'
        write_to_syslog(syslog.LOG_ERR, error_message)
        return

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        error_message = f'Error while updating the IP:{os.linesep * 2}{response.text}'
        write_to_syslog(syslog.LOG_ERR, error_message)
        return

    response = response.json()

    if response['success']:
        info_message = f'Host {host_name} new IP: {public_ip}'
        write_to_syslog(syslog.LOG_INFO, info_message)
        return
    else:
        error_message = f'Error while updating the IP:{os.linesep * 2}{json.dumps(response, indent=4)}'
        write_to_syslog(syslog.LOG_ERR, error_message)
        return


def write_to_syslog(level, message, telegram_message=True, disable_telegram_notification=False):
    if level == syslog.LOG_ERR:
        level_string = 'ERR'
    elif level == syslog.LOG_WARNING:
        level_string = 'WRN'
    elif level == syslog.LOG_INFO:
        level_string = 'INF'
    else:
        level_string = '---'

    syslog.syslog(level, f'{level_string} - {message}')
    if telegram_message:
        send_telegram_message(message, disable_telegram_notification)


if __name__ == '__main__':
    main()
