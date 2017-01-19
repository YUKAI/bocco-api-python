# encoding: utf-8
from __future__ import absolute_import
import os
from uuid import UUID
import hashlib

from flask import Flask, send_from_directory, url_for, request, redirect

from .models import Room, UUIDSchema
from . import api


#: Flask application
app = Flask(__name__)
app.api = None


@app.route('/')
def index():
    out = []
    app.logger.debug(u'Getting rooms...')
    rooms = app.api.get_rooms()
    template = u'<li><a href="/{room[uuid]}">{room[name]}</a></li>'
    return CSS + u'<h1>ROOMS</h1>' + u''.join([template.format(room=r) for r in rooms])


@app.route('/favicon.ico')
def favicon():
    return u''


@app.route('/<uuid>')
def room(uuid):
    uuid = UUIDSchema.validate(uuid)
    app.logger.debug(u'Getting room {0}...'.format(uuid))
    rooms = app.api.get_rooms()
    room = None
    for item in rooms:
        if uuid == item['uuid']:
            room = item

    if not room:
        return u'Room not found'
    return CSS + u'''
      <a href="/">&lt;= Rooms</a>
      <h1>{room[name]}</h1>
      <form method="post" action="/{room[uuid]}/messages/send" target="messages">
        <textarea name="text" placeholder="message"></textarea>
        <input type="submit" value="Submit" />
      </form>
      <iframe name="messages" src="/{room[uuid]}/messages"></iframe>
    '''.format(room=room)


@app.route('/<uuid>/messages')
def messages(uuid):
    uuid = UUIDSchema.validate(uuid)
    app.logger.debug(u'Getting messages in {0}...'.format(uuid))
    messages = app.api.get_messages(uuid)
    template = u'''
        <tr>
          <th>{user}</th>
          <td>{message[text]}</td>
          <td>{audio}</td>
          <td>{image}</td>
          <td>{message[media].name}</td>
          <td>{date}</td>
        </tr>
    '''.strip()
    items = []
    for message in messages[-min(len(messages), 10):]:
        image = audio = u''
        user = message['user']['nickname']
        if message['user']['icon']:
            user = u'<img src="/assets/{0}" width="32" height="32" alt="{1}" title="{1}" />'.format(
                        _get_assets_filename(message['user']['icon']),
                        message['user']['nickname'])
        if message['image']:
            image = u'<img src="/assets/{0}" />'.format(_get_assets_filename(message['image']))
        if message['audio']:
            audio = u'<a href="/assets/{0}">{1}</a>'.format(
                    _get_assets_filename(message['audio']),
                    os.path.basename(message['audio']))
        items.append(template.format(message=message,
                                     date=message['date'].humanize(),
                                     user=user,
                                     image=image,
                                     audio=audio))

    return u'<head><meta http-equiv="refresh" content="10"></head>' + CSS + u'''
      <table>
        <thead>
          <tr>
            <th>User</th>
            <th>Text</th>
            <th>Audio</th>
            <th>Image</th>
            <th>Media</th>
            <th>Date</th>
          </tr>
        </thead>
        <tbody>{body}</tbody>
      </table>'''.format(uuid=uuid, body=''.join(items))


@app.route('/<uuid>/messages/send', methods=['POST'])
def send(uuid):
    uuid = UUIDSchema.validate(uuid)
    app.logger.debug(u'Posting message to {0}...'.format(uuid))
    app.api.post_text_message(uuid, request.form['text'])
    return redirect(url_for('.messages', uuid=uuid))


@app.route('/assets/<filename>')
def assets(filename):
    return send_from_directory(app.config['DOWNLOADS'], filename)


def _get_assets_filename(url):
    md5 = hashlib.md5()
    md5.update(url.encode('utf-8'))
    digest = md5.hexdigest()
    _, ext = os.path.splitext(url)
    filename = digest + ext
    filepath = os.path.join(app.config['DOWNLOADS'], filename)
    if not os.path.isfile(filepath):
        app.logger.debug(u'Downloading {0}...'.format(url))
        app.api.download(url, filepath)
    return filename


CSS = u'''
<style>
body {
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  font-family: sans-serif;
  padding: 1rem;
}
table {
  width: 100%;
  font-size: 12px;
}
table, tr, th, td {
  border-collapse: collapse;
}
table thead tr {
  background-color: #ccc;
}
tr {
  background-color: #eee;
  border: 2px solid #fff;
}
image {
  max-width: 200px;
}
th, td {
  padding: .5rem .3rem;
}
iframe {
  width: 100%;
  height: 800px;
  border: 0px;
}
form {
  max-width: 80%;
  margin-left: auto;
  margin-right: auto;
  background-color: #eee;
  padding: .5rem;
}
form input[type=submit] {
  display: block;
  font-size: 2rem;
  margin-top: .5rem;
}
textarea {
  font-size: 1.5rem;
  display: block;
  width: 100%;
  height: 4rem;
}
</style>
'''
