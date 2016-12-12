from uuid import UUID

from typing import Any
from enum import Enum
from schema import Schema, And, Or, Use, Optional
import arrow


class UserType(Enum):
    HUMAN = u'human'
    BOCCO = u'bocco'
    SENSOR_DOOR = u'sensor_door'
    SENSOR_LOCK = u'sensor_lock'
    UNKNOWN = u''


class Seller(Enum):
    DMM = u'dmm'
    FOX = u'fox'
    KICKSTARTER = u'kickstarter'
    UNKNOWN = u'unknown'
    UNSET = u''


class MessageMedia(Enum):
    TEXT = u'text'
    AUDIO = u'audio'
    IMAGE = u'image'


class MessageType(Enum):
    NORMAL = u'normal'
    SYSTEM_SENSOR_JOINED = u'system.sensor_joined'
    SYSTEM_HUMAN_JOINED = u'system.human_joined'


URLSchema = And(str, lambda v: v.startswith(u'http://') or v.startswith(u'https://') or v == u'')

UUIDSchema = Or(UUID, Use(UUID))

DateTimeSchema = Or(arrow.Arrow, Use(arrow.get))


class _Model(object):

    schema = Schema(None)

    @classmethod
    def validate(cls, data: dict) -> dict:
        return cls.schema.validate(data)

    @classmethod
    def is_list(cls, l: Any) -> bool:
        if l is None:
            return False
        if len(l) == 0:
            return True
        for i in l:
            if type(i) != cls:
                return False
        return True

    def __init__(self, data: dict) -> None:
        cls = type(self)
        self._data = cls.validate(data)  # type: Dict[str, Any]

    def __getitem__(self, key):
        return self._data[key]

    def __repr__(self):
        return '<{0} {1}>'.format(type(self).__name__, self._data)


class User(_Model):
    """User model

    The instance is BOCCO or sensor or human user.

    >>> u = User({
    ...     'uuid': u'7b44ddd8-d1b0-4666-a11d-4dac68068ebd',
    ...     'user_type': u'bocco',
    ...     'nickname': u'TEST USER',
    ...     'seller': u'kickstarter',
    ...     'address': u'00:11:22:33:44:55',
    ...     'icon': u'http://example.com/image.png'
    ... })
    >>> u['uuid']
    UUID('7b44ddd8-d1b0-4666-a11d-4dac68068ebd')
    >>> u['user_type']
    <UserType.BOCCO: u'bocco'>
    >>> u['nickname']
    u'TEST USER'
    >>> u['seller']
    <Seller.KICKSTARTER: u'kickstarter'>
    >>> u['icon']
    u'http://example.com/image.png'
    """

    schema = Schema({
        'uuid': UUIDSchema,
        'user_type': Or(UserType, Use(UserType)),
        'nickname': And(str, lambda v: 0 <= len(v) < 120),
        'seller': Or(Seller, Use(Seller)),
        Optional('address'): str,
        Optional('icon'): URLSchema,
    }, ignore_extra_keys=True)


class RoomUser(_Model):
    """User on a room

    >>> u = RoomUser({
    ...     'read_id': 123,
    ...     'joined_at': '2015-01-02',
    ...     'user': {
    ...         'uuid': u'7b44ddd8-d1b0-4666-a11d-4dac68068ebd',
    ...         'user_type': u'bocco',
    ...         'nickname': u'TEST USER',
    ...         'seller': u'kickstarter',
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
    """The room is only connected to a BOCCO

    >>> r = Room({
    ...     'uuid': u'3e6aceea-4db1-44a3-b2a9-4ccfccd843e1',
    ...     'name': u'TEST ROOM',
    ...     'updated_at': u'2011-02-03',
    ...     'members': [
    ...         {
    ...             'read_id': 123,
    ...             'joined_at': u'2010-01-02',
    ...             'user': {
    ...                 'uuid': u'7b44ddd8-d1b0-4666-a11d-4dac68068ebd',
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
    ...             'seller': u'kickstarter',
    ...             'address': u'00:11:22:33:44:55',
    ...             'icon': u'http://example.com/image.png'
    ...         }
    ...     ]
    ... })
    >>> r['uuid']
    UUID('3e6aceea-4db1-44a3-b2a9-4ccfccd843e1')
    >>> r['name']
    u'TEST ROOM'
    >>> r['updated_at']
    <Arrow [2011-02-03T00:00:00+00:00]>
    >>> r['members'][0]['user']['nickname']
    u'TEST USER'
    >>> r['sensors'][0]['user_type']
    <UserType.SENSOR_DOOR: u'sensor_door'>
    """

    schema = Schema({
        'uuid': UUIDSchema,
        'name': And(str, lambda v: 0 < len(v) < 120),
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
    """Session

    >>> s = Session({
    ...     'access_token': u'Dummy Token',
    ...     'uuid': u'17023f65-065f-41e4-b648-cdd38076a7c9',
    ... })
    >>> s['access_token']
    u'Dummy Token'
    >>> s['uuid']
    UUID('17023f65-065f-41e4-b648-cdd38076a7c9')
    """

    schema = Schema({
        'access_token': str,
        'uuid': UUIDSchema,
    }, ignore_extra_keys=True)


class Message(_Model):
    """Message that sent to a room

    >>> m = Message({
    ...     'id': 123,
    ...     'dictated': True,
    ...     'unique_id': u'a8852948-fc6e-40d4-a384-e4c6a63b705e',
    ...     'media': u'text',
    ...     'audio': u'',
    ...     'message_type': u'normal',
    ...     'text': u'MESSAGE TEXT',
    ...     'image': u'',
    ...     'sender': u'0a0f6b39-ac63-4731-9c94-756ae80dd0b9',
    ...     'date': u'2016-03-02 11:00:59',
    ...     'user': {
    ...         'uuid': u'0a0f6b39-ac63-4731-9c94-756ae80dd0b9',
    ...         'user_type': u'bocco',
    ...         'nickname': u'TEST USER',
    ...         'seller': u'kickstarter',
    ...         'address': u'00:11:22:33:44:55',
    ...         'icon': u'http://example.com/image.png'
    ...     }
    ... })
    >>> m['id']
    123
    >>> m['dictated']
    True
    >>> m['user']['uuid']
    UUID('0a0f6b39-ac63-4731-9c94-756ae80dd0b9')
    """

    schema = Schema({
        'id': int,
        'dictated': bool,
        'unique_id': UUIDSchema,
        'media': Or(MessageMedia, Use(MessageMedia)),
        'audio': URLSchema,
        'message_type': Or(MessageType, Use(MessageType)),
        'text': str,
        'image': URLSchema,
        'sender': UUIDSchema,
        'date': DateTimeSchema,
        'user': Or(User, Use(User)),
    }, ignore_extra_keys=True)


class ApiErrorBody(_Model):
    """Response body for BOCCO API error

    >>> e = ApiErrorBody({
    ...     'code': 401,
    ...     'message': u'ERROR MESSAGE'
    ... })
    >>> e['code']
    401
    >>> e['message']
    u'ERROR MESSAGE'
    """

    schema = Schema({
        'code': int,
        'message': str,
    }, ignore_extra_keys=True)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
