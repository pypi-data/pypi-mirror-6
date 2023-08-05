#!/usr/bin/env python

"""Python client library for the Pushd server.

This client library is designed to support the Pushd API.
Read more about Pushd at http://github.com/rs/pushd/.

Basic usage:

from iscool_e.bellman import pushd
api = pushd.API()
api.createSubscriber('apns', 'token')

"""

import requests

class API(object):

    def __init__(self, host='localhost', port=None, timeout=None):
        if port:
            self.host = host + ':' + str(port)
        else:
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
        return self.request('event/' + event, post_args=args, method='POST')

    def createSubscriber(self, proto, token, lang='fr', badge=0):
        """Registers a device and returns an id for further communication"""
        data = {
            "proto": proto,
            "token": token,
            "lang": lang,
            "badge": badge,
        }
        return self.request('subscribers', post_args=data, method='POST')
    
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
        return self.request('subscriber/' + id, post_args=data, method='POST')
        
    def getSubscriber(self, id):
        """Get informations about a subscriber."""
        return self.request('subscriber/' + id)

    def deleteSubscriber(self, id):
        """Deletes a device using pushd generated id"""
        return self.request('subscriber/' + id, method='DELETE')

    def subscribe(self, id, event, ignore_message=False):
        """Subscribes to an event."""
        if ignore_message:
            post_args = {"ignore_message": 1}
        else:
            post_args = {}
        return self.request('subscriber/' + id + '/subscriptions/' + event, post_args=post_args, method='POST')

    def bulkSubscribe(self, id, events):
        """Subscribe to multiple events. Taking dictionary."""
        headers = {'Content-type': 'application/json'}
        return self.request('subscriber/' + id + '/subscriptions', post_args=events, headers=headers, method='POST')

    def unsubscribe(self, id, event):
        """Unsubscribe from an event."""
        return self.request('subscriber/' + id + '/subscriptions/' + event, method='DELETE')

    def getSubscriptions(self, id):
        """Fetchs subscriptions of a subscriber"""
        return self.request('subscriber/' + id + '/subscriptions')

    def checkSubscription(self, id, event):
        """Fetch only one subscription of a subscriber to check existence"""
        return self.request('subscriber/' + id + '/subscriptions/' + event)

    def request(self, path, args=None, post_args=None, files=None, headers=None, method=None):
        args = args or {}
        try:
            r = requests.request(method or "GET",
                                 "http://" + self.host + "/" + path, 
                                 timeout=self.timeout,
                                 params=args,
                                 data=post_args,
                                 files=files,
                                 headers=headers)
            if r.status_code in [201, 204]:
                response = {
                    "result": "ok",
                }
            elif 'json' in r.headers['content-type']:
                response = r.json()
            else:
                response = {
                    "error": {
                        "code": 404,
                    }
                }
        except requests.HTTPError, e:
            response = {
                "error": {
                    "code": e.status_code,
                }
            }

        return response
