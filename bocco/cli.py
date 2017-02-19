# encoding: utf-8
from __future__ import absolute_import
import os
import sys
import uuid
import json

import click

from .api import Client, ApiError
from .web import app
from io import open


def main():
    # type: () -> click.Command
    return cli(obj={})


@click.group()
@click.option('--config', type=click.Path(exists=True), default='config.json')
@click.option('--access-token')
@click.pass_context
def cli(ctx, config, access_token):
    # type: (click.Context, str, str) -> None
    """BOCCO API http://api-docs.bocco.me/ を CLI で操作するツール"""
    debug = False
    downloads = None
    if config:
        with open(config, 'r') as f:
            config_json = json.load(f)
            debug = config_json['debug']
            downloads = config_json['downloads']
            access_token = config_json['access_token']

    ctx.obj['api'] = Client(access_token)
    ctx.obj['debug'] = debug
    ctx.obj['downloads'] = downloads


@cli.command()
@click.option('-v', '--verbose', is_flag=True)
@click.pass_context
def rooms(ctx, verbose):
    # type: (click.Context, bool) -> None
    """部屋一覧を表示"""
    api = ctx.obj['api']
    template = u'{index}. {r[name]}\n\t{r[uuid]}'
    if verbose:
        template = u'''
{index}. {r[name]}
\tuuid: {r[uuid]}
\tmembers({members_count}): {members}
\tsensors({sensors_count}): {sensors}
\tupdated_at: {r[updated_at]}
'''.strip()

    for i, r in enumerate(api.get_rooms()):
        member_names = [m['user']['nickname'] for m in r['members']]
        sensor_names = [s['nickname'] for s in r['sensors']]
        click.echo(template.format(
                index=i + 1,
                r=r,
                members_count=len(member_names),
                members=u', '.join(member_names),
                sensors_count=len(sensor_names),
                sensors=u', '.join(sensor_names)))


@cli.command()
@click.argument('room_uuid')
@click.option('-n', '--newer_than', default=0, type=int)
@click.option('-o', '--older_than', default=0, type=int)
@click.option('-l', '--limit', default=10, type=int)
@click.option('-v', '--verbose', is_flag=True)
@click.pass_context
def messages(ctx,
             room_uuid,
             newer_than,
             older_than,
             limit,
             verbose):
    # type: (click.Context, str, int, int, int, bool) -> None
    """指定した部屋のメッセージを表示"""
    api = ctx.obj['api']
    messages = api.get_messages(uuid.UUID(room_uuid),
                                newer_than=newer_than,
                                older_than=older_than)
    template = u'{m[date]} {m[user][nickname]} {m[text]}'
    if verbose:
        template = u'''
{m[date]} {m[user][nickname]} {m[text]}
\tid: {m[id]}
\tunique_id: {m[unique_id]}
\tmedia: {m[media]}
\tmessage_type: {m[message_type]}
\tdictated: {m[dictated]}
'''.strip()
    for m in messages[-limit:]:
        click.echo(template.format(m=m))


@cli.command()
@click.argument('room_uuid')
@click.argument('text')
@click.pass_context
def send(ctx, room_uuid, text):
    # type: (click.Context, str, str) -> None
    """テキストメッセージを送信."""
    api = ctx.obj['api']
    click.echo(u'メッセージ送信中...')
    api.post_text_message(uuid.UUID(room_uuid), text)


@cli.command()
@click.pass_context
def web(ctx):
    # type: (click.Context) -> None
    """Web サーバ上で API クライアントを起動"""
    api = ctx.obj['api']
    debug = ctx.obj['debug']
    downloads = ctx.obj['downloads']

    app.config.update(dict(DEBUG=debug, DOWNLOADS=downloads))
    app.api = api
    app.run()

