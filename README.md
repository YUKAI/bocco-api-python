# bocco-api-python

Python 3 系で動作します。

API ドキュメント: https://yukai.github.io/bocco-api-python/

## Setup

```
$ git clone https://github.com/YUKAI/bocco-api-python.git
$ cd bocco-api-python
$ pip install -r requirements.txt
```


## Example

```python
api = bocco.api.Client('API KEY')
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
  --api-key TEXT
  --email TEXT
  --password TEXT
  --help           Show this message and exit.

Commands:
  messages  Show messages in the room.
  rooms     Show joined rooms.
  send      Send text message.
```
