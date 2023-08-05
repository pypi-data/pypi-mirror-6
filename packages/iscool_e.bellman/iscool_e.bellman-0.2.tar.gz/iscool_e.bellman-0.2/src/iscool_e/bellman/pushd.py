#!/usr/bin/env python

"""Python client library for the Pushd server.

This client library is designed to support the Pushd API.
Read more about Pushd at http://github.com/rs/pushd/.

Basic usage:

from iscool_e.bellman import pushd
api = pushd.API()
api.createSubscriber('apns', 'token')

"""

import urllib
import urllib2
import httplib
import json

class API(object):

    def __init__(self, host='localhost', timeout=None):
        self.host = host
        self.timeout = timeout

    def sendMessage(self, event, message, localized_messages={}, vars={}, data={}, sound=None):
        """Broadcasts a message to an event (channel)

           Variable placeholders in messages shoud be used this way :
           "Hello {name}!"

           event: Event name where to broadcast the message
           message: Default message used if device "lang" does not match in localized_messages
           localized_messages: Dict (translated messages) {"fr":"Bonjour", "en":"Hello"}
           vars:  Dict (strings to be reused in every message)
           data:  Dict (custom data to send to the app) {"foo":"bar"}
           sound: Name of a sound file to be played
                  It must match a sound file name contained in your bundled app (iOS only)
        """
        args = {"msg": message}
        for lang, msg in localized_messages.items():
            args['msg.' + lang] = msg.format(**vars)
        for key, value in data.items():
            args['data.' + key] = value
        if sound:
            args['sound'] = sound
        return self.request('event/' + event, post_args=args)

    def createSubscriber(self, proto, token, lang='fr', badge=0):
        """Registers a device and returns an id for further communication"""
        data = {
            "proto": proto,
            "token": token,
            "lang": lang,
            "badge": badge,
        }
        return self.request('subscribers', post_args=data)
    
    def updateSubscriber(self, id, lang='fr', badge=0):
        """Ping to let pushd know the subscriber still exists
           On iOS, you must update the badge value to inform pushd
           the user read the pending notifications, maybe each time
           the badge is updated
        """
        data = {
            "lang": lang,
            "badge": badge,
        }
        return self.request('subscriber/' + id, post_args=data)
        
    def getSubscriber(self, id):
        """Get informations about a subscriber."""
        return self.request('subscriber/' + id)

    def deleteSubscriber(self, id):
        """Deletes a device using pushd generated id"""
        conn = httplib.HTTPConnection(self.host)
        conn.request('DELETE', '/subscriber/' + id)
        resp = conn.getresponse()
        return resp.read()

    def subscribe(self, id, event, ignore_message=False):
        """Subscribes to an event."""
        if ignore_message:
            post_args = {"ignore_message": 1}
        else:
            post_args = {}
        return self.request('subscriber/' + id + '/subscriptions/' + event, post_args=post_args)

    def bulkSubscribe(self, id, events):
        """Subscribe to multiple events. Taking dictionary."""
        return self.request('subscriber/' + id + '/subscriptions', post_args=events)

    def unsubscribe(self, id, event):
        """Unsubscribe from an event."""
        conn = httplib.HTTPConnection(self.host)
        conn.request('DELETE', '/subscriber/' + id + '/subscriptions/' + event)
        resp = conn.getresponse()
        return resp.read()

    def getSubscriptions(self, id):
        """Fetchs subscriptions of a subscriber"""
        return self.request('subscriber/' + id + '/subscriptions')

    def checkSubscription(self, id, event):
        """Fetch only one subscription of a subscriber to check existence"""
        return self.request('subscriber/' + id + '/subscriptions/' + event)

    def request(self, path, args=None, post_args=None):
        args = args or {}
        post_data = None if post_args is None else urllib.urlencode(post_args)
        try:
            data = urllib2.urlopen("http://" + self.host + "/" + path + "?" +
                                   urllib.urlencode(args),
                                   post_data, timeout=self.timeout)
            if data.code in [201, 204]:
                response = {
                    "result": "ok",
                }
            else:
                response = json.loads(data.read())
        except urllib2.HTTPError, err:
            response = {
                "error": {
                    "code": err.code,
                }
            }
        except TypeError:
            if self.timeout:
                socket.setdefaulttimeout(self.timeout)
            data = urllib2.urlopen("http://" + self.host + "/" + path + "?" +
                                   urllib.urlencode(args), post_data)
            response = json.loads(data.read())

        return response
