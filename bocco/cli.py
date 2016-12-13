import os
import uuid
import json

import click

from .api import Client, ApiError
from .web import app


def main() -> click.Command:
    return cli(obj={})


@click.group()
@click.option('--config', type=click.Path(exists=True), default='config.json')
@click.option('--api-key')
@click.option('--email')
@click.option('--password')
@click.pass_context
def cli(ctx: click.Context, config: str, api_key: str, email: str, password: str) -> None:
    """BOCCO API http://api-docs.bocco.me/ ."""
    debug = False
    downloads = None
    if config:
        with open(config, 'r') as f:
            config_json = json.load(f)
            api_key = config_json['api_key']
            email = config_json['email']
            password = config_json['password']
            downloads = config_json['downloads']
            debug = config_json['debug']

    assert api_key, 'api_key must not be null'
    assert email, 'email must not be null'
    assert password, 'password must not be null'

    ctx.obj['debug'] = debug
    ctx.obj['api'] = Client(api_key)
    ctx.obj['downloads'] = downloads
    click.echo(u'Signing in...')
    try:
        ctx.obj['api'].signin(email, password)
    except ApiError as e:
        click.echo(e)


@cli.command()
@click.option('-v', '--verbose', is_flag=True)
@click.pass_context
def rooms(ctx: click.Context, verbose: bool) -> None:
    """Show joined rooms."""
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
def messages(ctx: click.Context,
             room_uuid: str,
             newer_than: int,
             older_than: int,
             limit: int,
             verbose: bool) -> None:
    """Show messages in the room."""
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
def send(ctx: click.Context, room_uuid: str, text: str) -> None:
    """Send text message."""
    api = ctx.obj['api']
    click.echo('Sending text message...')
    api.post_text_message(uuid.UUID(room_uuid), text)


@cli.command()
@click.pass_context
def web(ctx: click.Context) -> None:
    """Run API client on web server."""
    api = ctx.obj['api']
    debug = ctx.obj['debug']
    downloads = ctx.obj['downloads']

    app.config.update(dict(DEBUG=debug, DOWNLOADS=downloads))
    app.api = api
    app.run()

