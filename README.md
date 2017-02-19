# bocco-api-python

[![wercker status](https://app.wercker.com/status/4c4b21fefec1c211cd3961f72d1b9078/s/master "wercker status")](https://app.wercker.com/project/byKey/4c4b21fefec1c211cd3961f72d1b9078)

Python 2, 3 系で動作します。

ドキュメント: https://yukai.github.io/bocco-api-python/

## セットアップ

```
$ git clone https://github.com/YUKAI/bocco-api-python.git
$ cd bocco-api-python
$ pip install -r requirements.txt
```


## サンプル

```python
api = bocco.api.Client('ACCESS TOKEN')
# or api = bocco.api.Client.signin('API KEY', 'test@example.com', 'pass')

# Post a message to all rooms.
for room in api.get_rooms()
    api.post_text_message(room['uuid'], 'hello')
```


## コマンドラインツール

```
$ python bin/boccotools.py 
Usage: boccotools.py [OPTIONS] COMMAND [ARGS]...

  BOCCO API http://api-docs.bocco.me/ .

Options:
  --config PATH
  --access-token TEXT
  --help               Show this message and exit.

Commands:
  messages  Show messages in the room.
  rooms     Show joined rooms.
  send      Send text message.
  web       Run API client on web server.
```
