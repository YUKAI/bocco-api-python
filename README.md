# BOCCO API python SDK

http://api-docs.bocco.me/

Python 3 系で動作します。

## Setup

```
$ cd bocco-api-python
$ pip install -r requirements.txt
```


## Example

```python
api = bocco.api.Client('token')
api.signin('test@example.com', 'password')
# Post a message to all rooms.
for room in api.get_rooms()
    api.post_text_message(room['uuid'], 'hello')
```


## Command line tool

```
$ python bin/boccotools.py 
Usage: boccotools.py [OPTIONS] COMMAND [ARGS]...

  BOCCO API http://api-docs.bocco.me/ .

Options:
  --config PATH
  --token TEXT
  --email TEXT
  --password TEXT
  --help           Show this message and exit.

Commands:
  messages  Show messages in the room.
  rooms     Show joined rooms.
  send      Send text message.
  web       Run API client on web server.
```

