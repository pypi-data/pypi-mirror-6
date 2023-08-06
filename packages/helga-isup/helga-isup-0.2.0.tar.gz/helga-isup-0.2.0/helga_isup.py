import re

import requests

from twisted.internet import reactor

from helga.plugins import command, ResponseNotReady


def do_isup(client, channel, domain):
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
    client.msg(channel, status.replace('&#x2F;', '/'))


@command('isup', aliases=['downforeveryoneorjustme'],
         help='Is foo.com up? Usage: helga [isup|downforeveryoneorjustme] <domain>')
def isup(client, channel, nick, message, cmd, args):
    reactor.callLater(0, do_isup, client, channel, args[0])
    raise ResponseNotReady
