import re

import requests

from helga.plugins import command


@command('isup', aliases=['downforeveryoneorjustme'],
         help='Is foo.com up? Usage: helga [isup|downforeveryoneorjustme] <domain>')
def isup(client, channel, nick, message, cmd, args):
    domain = args[0]

    resp = requests.get('http://isup.me/{domain}'.format(domain=domain))
    resp.raise_for_status()

    # Find the content we want
    status = re.findall(r'<div id="container">(.*?)<p>', resp.content.replace('\n', ''))
    status = status[0].strip()

    # Strip tags
    status = re.sub(r'<.*?>', '', status)

    # Fix extra spaces
    status = re.sub(r'[\s]+', ' ', status)

    # Strip entities
    return status.replace('&#x2F;', '/')
