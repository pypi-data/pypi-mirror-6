# -*- encoding: utf-8 -*-
import hashlib
import hmac
import requests
import json
from datetime import datetime
import logging

logger = logging.getLogger('RT_Client')


class RT_Client(object):
    ''' Client for RuuviTracker API v1 '''
    API_VERSION = 1
    USER_AGENT = 'RuuviTracker Python Client API v1/0.1'

    def __init__(self, tracker_code, shared_secret, url, session_code=None):
        ''' Initialize RuuviTracker Client '''
        self.tracker_code = tracker_code
        self.shared_secret = shared_secret
        self.url = url
        self.session_code = session_code

    def __mac_input(self, data):
        ''' Generate input for HMac calculation '''
        m = ''
        for key in sorted(data.iterkeys()):
            value = data[key]
            m += key
            m += ':'
            m += str(value)
            m += '|'
        logger.debug('macInput: %s' % m)
        return m

    def __make_query(self, data):
        ''' Make query to RuuviTracker server '''
        headers = {
            'User-Agent': self.USER_AGENT,
            'Content-type': 'application/json'
        }
        logger.debug('Sending data: %s' % json.dumps(data))
        r = requests.post(self.url, headers=headers, data=json.dumps(data))
        logger.debug('Server response: %s (%s)' % (r.status_code, r.text))
        return r.status_code

    def _compute_hmac(self, data):
        ''' Calculate HMac for message '''
        digest = hmac.new(self.shared_secret, digestmod=hashlib.sha1)
        digest.update(self.__mac_input(data))
        return digest.hexdigest()

    def _create_message(self, data):
        ''' Create message to send to server '''
        data['version'] = self.API_VERSION
        data['tracker_code'] = self.tracker_code
        data['mac'] = self._compute_hmac(data)
        return data

    def send_message(self, data):
        ''' Sends message to server. Argument "data" must be an instance of RT_Data '''
        if not isinstance(data, RT_Data):
            logger.error('Incompatible datatype, use RT_Data')
            return

        data = self._create_message(data.build_data())
        return self.__make_query(data)


class RT_Data(object):
    ''' Data instance for RuuviTracker '''
    def __init__(
            self, latitude=None, longitude=None, time=None,
            accuracy=None, vertical_accuracy=None, heading=None,
            satellite_count=None, battery=None, speed=None,
            altitude=None, temperature=None, annotation=None,
            extra=dict()):
        self.latitude = latitude
        self.longitude = longitude
        self.time = time
        self.accuracy = accuracy
        self.vertical_accuracy = vertical_accuracy
        self.heading = heading
        self.satellite_count = satellite_count
        self.battery = battery
        self.speed = speed
        self.altitude = altitude
        self.temperature = temperature
        self.annotation = annotation
        self.extra = extra

    def build_data(self):
        ''' Builds data-dictionary suitable for RuuviTracker server '''
        def remove_non_ascii(s):
            return "".join(i for i in s if ord(i) < 128).replace(' ', '-')

        data = dict()
        # latitude can be a float (62.8723) or string (6284.21,N)
        if self.latitude is not None:
            data['latitude'] = self.latitude
        # longitude can be a float (28.8723) or string (2884.21,N)
        if self.longitude is not None:
            data['longitude'] = self.longitude
        if self.time is not None:
            # if instance of datetime is passed, format it according to the spec
            if type(self.time) == datetime:
                data['time'] = self.time.strftime('%Y-%m-%dT%H:%M:%S.000%z')
            # else trust that the user has done the required measures to format it
            else:
                data['time'] = str(self.time)
        if self.accuracy is not None:
            data['accuracy'] = float(self.latitude)
        if self.vertical_accuracy is not None:
            data['vertical_accuracy'] = float(self.vertical_accuracy)
        if self.heading is not None:
            data['heading'] = float(self.heading)
        if self.satellite_count is not None:
            data['satellite_count'] = int(self.satellite_count)
        if self.battery is not None:
            data['battery'] = float(self.battery)
        if self.speed is not None:
            data['speed'] = float(self.speed)
        if self.altitude is not None:
            data['altitude'] = float(self.altitude)
        if self.temperature is not None:
            data['temperature'] = float(self.temperature)
        if self.annotation is not None:
            data['annotation'] = str(self.annotation)
        if self.extra and type(self.extra) == dict:
            for k, v in self.extra.iteritems():
                k = remove_non_ascii(k)
                if k.startswith('X-'):
                    data['%s' % k] = v
                else:
                    data['X-%s' % k] = v
        return data
