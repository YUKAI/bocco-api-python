# encoding: utf-8
from __future__ import absolute_import
import sys
import uuid

try:
    from typing import Any, Dict, List, Optional, Type, Tuple
except:
    pass

import requests
from schema import SchemaError

from .models import ApiErrorBody, Session, Room, Message, MessageMedia
from io import open


if (3, 0) <= sys.version_info:
    unicode = str

BASE_URL = 'https://api.bocco.me/alpha'


class Client(object):
    """BOCCO API Client"""

    @classmethod
    def signin(cls, api_key, email, password):
        # type: (str, str, str) -> Client
        """Create client with new session

        Web API: http://api-docs.bocco.me/reference.html#post-sessions
        """
        data = {'apikey': api_key,
                'email': email,
                'password': password}
        r = requests.post(BASE_URL + '/sessions', data=data)
        session = Client._parse(r.json(), Session)
        return Client(session['access_token'])

    @classmethod
    def _parse(cls, data, klass):
        # type: (Dict[str, Any], Type[Any]) -> Any
        try:
            return klass(data)
        except SchemaError as e:
            pass
        body = ApiErrorBody(data)
        raise ApiError(body)

    def __init__(self, access_token):
        # type: (str) -> None
        self.access_token = access_token  # type: str
        self.headers = {'Accept-Language': 'ja-JP,ja'}  # type: dict

    def _post(self, path, data):
        # type: (str, Optional[Dict[str, Any]]) -> requests.Response
        if data is None:
            data = {}
        if 'access_token' not in data:
            data['access_token'] = self.access_token
        return requests.post(BASE_URL + path,
                             data=data,
                             headers=self.headers)

    def _get(self, path, params = None):
        # type: (str, Optional[Dict[str, Any]]) -> requests.Response
        if params is None:
            params = {}
        if 'access_token' not in params:
            params['access_token'] = self.access_token
        return requests.get(BASE_URL + path,
                            params=params,
                            headers=self.headers)

    def get_rooms(self):
        # type: () -> List[Room]
        """Get joined rooms

        Web API: http://api-docs.bocco.me/reference.html#get-roomsjoined
        """
        r = self._get('/rooms/joined')
        data = r.json()
        if type(data) != list:
            return []
        rooms = []
        for room_data in data:
            if room_data['sensors'] is None:
                room_data['sensors'] = []
            if room_data['members'] is None:
                room_data['members'] = []
            rooms.append(Room(room_data))
        return rooms

    def get_messages(self,
                     room_uuid,
                     newer_than = None,
                     older_than = None,
                     read = True):
        # type: (uuid.UUID, Optional[int], Optional[int], bool) -> List[Message]
        """Get messages

        Web API: http://api-docs.bocco.me/reference.html#get-roomsroomidmessages
        """
        assert type(room_uuid) == uuid.UUID
        r = self._get('/rooms/{0}/messages'.format(room_uuid),
                      params={'newer_than': newer_than,
                              'older_than': older_than,
                              'read': 1 if read else 0})
        data = r.json()
        if type(data) != list:
            return []
        messages = []
        for message_data in data:
            messages.append(Message(message_data))
        return messages

    def subscribe(self,
                  room_uuid,
                  newer_than = None,
                  read = True):
        # type: (uuid.UUID, Optional[int], bool) -> List[Message]
        """Subscribe messages

        Web API: http://api-docs.bocco.me/reference.html#get-roomsroomidsubscribe
        """
        assert type(room_uuid) == uuid.UUID
        r = self._get('/rooms/{0}/subscribe'.format(room_uuid),
                      params={'newer_than': newer_than,
                              'read': 1 if read else 0})
        data = r.json()
        if type(data) != list:
            return []
        messages = []
        for event in data:
            if event['event'] == u'message':
                messages.append(Message(event['body']))
            # TODO handle event['event'] == 'member'
        return messages

    def _post_message(self, room_uuid, data):
        # type: (uuid.UUID, Dict[str, str]) -> Message
        data.setdefault('text', '')
        data.setdefault('audio', '')
        data.setdefault('image', '')
        data.setdefault('unique_id', unicode(uuid.uuid4()))
        assert type(room_uuid) == uuid.UUID
        assert len(data['text']) < 10000
        r = self._post('/rooms/{0}/messages'.format(room_uuid), data=data)
        return Client._parse(r.json(), Message)

    def post_text_message(self, room_uuid, text):
        # type: (uuid.UUID, str) -> Message
        """Post text message

        Web API: http://api-docs.bocco.me/reference.html#post-roomsroomidmessages
        """
        data = {'text': text,
                'media': MessageMedia.text.value}
        return self._post_message(room_uuid, data)

    def post_audio_message(self, room_uuid, audio):
        # TODO: implement
        pass

    def post_image_message(self, room_uuid, image):
        # TODO: implement
        pass

    def download(self, url, dest):
        # type: (str, str) -> requests.Response
        """Download assets

        Web API: http://api-docs.bocco.me/reference.html#get-messagesuniqueidextname
        """
        params = {'access_token': self.access_token}
        r = requests.get(url,
                         params=params,
                         headers=self.headers,
                         stream=True)
        with open(dest, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return r


class ApiError(IOError):
    """API error response

    Web API: http://api-docs.bocco.me/reference.html#section-31
    """

    def __init__(self, body):
        # type: (ApiErrorBody) -> None
        self.body = body  # type: ApiErrorBody

    def __str__(self):
        return '<ApiError {0}: {1}>'.format(self.body['code'], self.body['message'])
