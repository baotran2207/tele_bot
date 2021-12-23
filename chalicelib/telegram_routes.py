import asyncio
import os
# import pandas as pd

from chalice import Blueprint

from telethon import TelegramClient, sync
from telethon.sessions import StringSession

bp_telegram = Blueprint(__name__)

api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')
group_username = os.getenv('group_username')
session_token = os.getenv('session_token')
#

@bp_telegram.route('/myinfo')
def myinfo():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = TelegramClient(StringSession(session_token), api_id, api_hash, loop=loop)
    client.start()

    me = client.get_me()
    print(me.stringify())
    return 'ok'

@bp_telegram.route('/participants')
def participants():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = TelegramClient(StringSession(session_token), api_id, api_hash, loop=loop)
    client.start()
    parts = client.get_participants('HCCapital_Chat')
    print(parts[0])
    print(type(parts[0]))
    return 'ok'


@bp_telegram.route('/get_messages')
def participants():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = TelegramClient(StringSession(session_token), api_id, api_hash, loop=loop)
    client.start()
    chats = client.get_messages('', 50)
    print(chats)
    return 'ok'