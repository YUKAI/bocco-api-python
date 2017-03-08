# encoding: utf-8
from __future__ import absolute_import
import sys
from uuid import UUID

try:
    from typing import Any
except:
    pass

from enum import Enum
from schema import Schema, And, Or, Use, Optional
import arrow

if (3, 0) <= sys.version_info:
    unicode = str


class UserType(Enum):
    """ユーザ種別"""
    human = 'human'
    bocco = 'bocco'
    sensor_door = 'sensor_door'
    sensor_lock = 'sensor_lock'
    unknown = 'unknown'


class MessageMedia(Enum):
    """メッセージのメディア"""
    text = 'text'
    audio = 'audio'
    image = 'image'
    stamp = 'stamp'
    unknown = 'unknown'


class MessageType(Enum):
    """メッセージの種別"""
    normal = 'normal'
    system_sensor_joined = 'system.sensor_joined'
    system_human_joined = 'system.human_joined'
    unknown = 'unknown'


URLSchema = And(unicode, lambda v: v.startswith('http://') or v.startswith('https://') or v == '')


UUIDSchema = Or(UUID, Use(UUID))


DateTimeSchema = Or(arrow.Arrow, Use(arrow.get))


class _Model(object):

    schema = Schema(None)

    @classmethod
    def validate(cls, data):
        # type: (dict) -> dict
        return cls.schema.validate(data)

    @classmethod
    def is_list(cls, l):
        # type: (Any) -> bool
        if l is None:
            return False
        if len(l) == 0:
            return True
        for i in l:
            if type(i) != cls:
                return False
        return True

    def __init__(self, data):
        # type: (dict) -> None
        cls = type(self)
        self._data = cls.validate(data)  # type: Dict[str, Any]

    def __getitem__(self, key):
        return self._data[key]

    def __repr__(self):
        return '<{0} {1}>'.format(type(self).__name__, self._data)


class User(_Model):
    """BOCCO ユーザ

    BOCCO 本体またはアプリユーザの情報。

    >>> u = User({
    ...     'uuid': u'7b44ddd8-d1b0-4666-a11d-4dac68068ebd',
    ...     'user_type': u'bocco',
    ...     'nickname': u'ニックネーム',
    ...     'seller': u'',
    ...     'address': u'00:11:22:33:44:55',
    ...     'icon': u'http://example.com/image.png'
    ... })
    >>> u['uuid']
    UUID('7b44ddd8-d1b0-4666-a11d-4dac68068ebd')
    >>> u['user_type'] == UserType.bocco
    True
    >>> u['nickname'] == u'ニックネーム'
    True
    >>> u['seller'] == u''
    True
    >>> u['icon'] == u'http://example.com/image.png'
    True
    """

    schema = Schema({
        'uuid': UUIDSchema,
        'user_type': Or(UserType, Use(UserType), Use(lambda v: UserType.unknown)),
        'nickname': And(unicode, lambda v: 0 <= len(v) < 120),
        'seller': unicode,
        Optional('address'): unicode,
        Optional('icon'): URLSchema,
    }, ignore_extra_keys=True)


class RoomUser(_Model):
    """部屋と紐付いたユーザ情報

    >>> u = RoomUser({
    ...     'read_id': 123,
    ...     'joined_at': u'2015-01-02',
    ...     'user': {
    ...         'uuid': u'7b44ddd8-d1b0-4666-a11d-4dac68068ebd',
    ...         'user_type': u'bocco',
    ...         'nickname': u'TEST USER',
    ...         'seller': u'',
    ...         'address': u'00:11:22:33:44:55',
    ...         'icon': u'http://example.com/image.png'
    ...     }
    ... })
    >>> u['read_id']
    123
    >>> u['joined_at']
    <Arrow [2015-01-02T00:00:00+00:00]>
    >>> u['user']['uuid']
    UUID('7b44ddd8-d1b0-4666-a11d-4dac68068ebd')
    """

    schema = Schema({
        'read_id': int,
        'joined_at': DateTimeSchema,
        'user': Or(User, Use(User)),
    }, ignore_extra_keys=True)


class Room(_Model):
    """部屋情報

    >>> r = Room({
    ...     'uuid': u'3e6aceea-4db1-44a3-b2a9-4ccfccd843e1',
    ...     'name': u'テストルーム',
    ...     'updated_at': u'2011-02-03',
    ...     'members': [
    ...         {
    ...             'read_id': 123,
    ...             'joined_at': u'2010-01-02',
    ...             'user': {
    ...                 'uuid': 'u7b44ddd8-d1b0-4666-a11d-4dac68068ebd',
    ...                 'user_type': u'human',
    ...                 'nickname': u'TEST USER',
    ...                 'seller': u'',
    ...                 'address': u'00:11:22:33:44:55',
    ...                 'icon': u'http://example.com/image.png'
    ...             }
    ...         }
    ...     ],
    ...     'sensors': [
    ...         {
    ...             'uuid': u'0af1c101-3b7d-40a8-9e63-bf03f2dda6c4',
    ...             'user_type': u'sensor_door',
    ...             'nickname': u'DOOR SENSOR',
    ...             'seller': u'',
    ...             'address': u'00:11:22:33:44:55',
    ...             'icon': u'http://example.com/image.png'
    ...         }
    ...     ]
    ... })
    >>> r['uuid']
    UUID('3e6aceea-4db1-44a3-b2a9-4ccfccd843e1')
    >>> r['name'] == u'テストルーム'
    True
    >>> r['updated_at']
    <Arrow [2011-02-03T00:00:00+00:00]>
    >>> r['members'][0]['user']['nickname'] == 'TEST USER'
    True
    >>> r['sensors'][0]['user_type'] == UserType.sensor_door
    True
    """

    schema = Schema({
        'uuid': UUIDSchema,
        'name': And(unicode, lambda v: 0 < len(v) < 120),
        'updated_at': DateTimeSchema,
        'members': Or(
            Use(lambda l: l or []),
            lambda l: RoomUser.is_list(l),
            Use(lambda l: [RoomUser(i) for i in l])),
        'sensors': Or(
            lambda l: User.is_list(l),
            Use(lambda l: [User(i) for i in l])),
    }, ignore_extra_keys=True)


class Session(_Model):
    """API クライアントのセッション情報

    >>> s = Session({
    ...     'access_token': u'Dummy Token',
    ...     'uuid': u'17023f65-065f-41e4-b648-cdd38076a7c9',
    ... })
    >>> s['access_token'] == u'Dummy Token'
    True
    >>> s['uuid']
    UUID('17023f65-065f-41e4-b648-cdd38076a7c9')
    """

    schema = Schema({
        'access_token': unicode,
        'uuid': UUIDSchema,
    }, ignore_extra_keys=True)


class Message(_Model):
    """部屋へ送信されたメッセージ

    >>> m = Message({
    ...     'id': 123,
    ...     'dictated': True,
    ...     'unique_id': u'a8852948-fc6e-40d4-a384-e4c6a63b705e',
    ...     'media': u'text',
    ...     'audio': u'',
    ...     'message_type': u'normal',
    ...     'text': u'メッセージです',
    ...     'image': u'',
    ...     'sender': u'0a0f6b39-ac63-4731-9c94-756ae80dd0b9',
    ...     'date': u'2016-03-02 11:00:59',
    ...     'user': {
    ...         'uuid': u'0a0f6b39-ac63-4731-9c94-756ae80dd0b9',
    ...         'user_type': u'bocco',
    ...         'nickname': u'ニックネーム',
    ...         'seller': u'',
    ...         'address': u'00:11:22:33:44:55',
    ...         'icon': u'http://example.com/image.png'
    ...     }
    ... })
    >>> m['id']
    123
    >>> m['text'] == u'メッセージです'
    True
    >>> m['dictated']
    True
    >>> m['user']['uuid']
    UUID('0a0f6b39-ac63-4731-9c94-756ae80dd0b9')
    """

    schema = Schema({
        'id': int,
        'dictated': bool,
        'unique_id': UUIDSchema,
        'media': Or(MessageMedia, Use(MessageMedia), Use(lambda v: MessageMedia.unknown)),
        'audio': URLSchema,
        'message_type': Or(MessageType, Use(MessageType), Use(lambda v: MessageType.unknown)),
        'text': unicode,
        'image': URLSchema,
        'sender': UUIDSchema,
        'date': DateTimeSchema,
        'user': Or(User, Use(User)),
    }, ignore_extra_keys=True)


class ApiErrorBody(_Model):
    """エラーレスポンス

    エラーコードの詳細は以下を参照
    http://api-docs.bocco.me/reference.html#section-31

    >>> e = ApiErrorBody({
    ...     'code': 401,
    ...     'message': u'ERROR MESSAGE'
    ... })
    >>> e['code']
    401
    >>> e['message'] == u'ERROR MESSAGE'
    True
    """

    schema = Schema({
        'code': int,
        'message': unicode,
    }, ignore_extra_keys=True)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
