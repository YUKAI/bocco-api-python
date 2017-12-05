==================
bocco-api-python
==================

.. image:: https://app.wercker.com/status/4c4b21fefec1c211cd3961f72d1b9078/s/master
   :target: https://app.wercker.com/project/byKey/4c4b21fefec1c211cd3961f72d1b9078

コミュニケーションロボット BOCCO を操作するための `BOCCO API <http://api-docs.bocco.me>`_
を Python から操作するためのライブラリです。

ドキュメント: https://yukai.github.io/bocco-api-python/

セットアップ
============

pip の場合::

    $ pip install bocco

setup.py の場合::

    $ git clone https://github.com/YUKAI/bocco-api-python.git
    $ cd bocco-api-python
    $ python setup.py install


サンプル
=========

::

    api = bocco.api.Client('ACCESS TOKEN')
    # 新しいセッションを開始する場合
    #api = bocco.api.Client.signin('API KEY', 'test@example.com', 'pass')
    #print(api.access_token)

    # 全ての部屋にメッセージを送る
    for room in api.get_rooms()
        api.post_text_message(room['uuid'], 'hello')


コマンドラインツール
======================

::

    Usage: boccotools.py [OPTIONS] COMMAND [ARGS]...

      BOCCO API http://api-docs.bocco.me/ を CLI で操作するツール

    Options:
      --config PATH
      --access-token TEXT
      --help               Show this message and exit.

    Commands:
      messages  指定した部屋のメッセージを表示
      rooms     部屋一覧を表示
      send      テキストメッセージを送信.
      web       Web サーバ上で API クライアントを起


バージョンアップ
===================

`/bocco/__init__.py`, `/bocco/__init__.py` のバージョンを更新する。
