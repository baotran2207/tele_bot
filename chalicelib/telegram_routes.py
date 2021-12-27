import asyncio
import os
# import pandas as pd
from chalice import Blueprint
from pprint import pprint


from telegram import Bot
from telethon import TelegramClient, sync
from telethon.sessions import StringSession
import yaml
from telethon.tl.types import ChannelParticipantsAdmins, InputMessagesFilterEmpty, PeerUser, PeerChannel
from telethon.tl import functions
from datetime import datetime, timedelta, timezone

with open(
    os.path.join(os.path.dirname(__file__),'following_groups.yaml',
    ), 'r') as f:
    following_groups = yaml.load(f,  Loader=yaml.FullLoader)


bp_telegram = Blueprint(__name__)

api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')
group_username = os.getenv('group_username')
session_token = os.getenv('session_token')

from dataclasses import dataclass, asdict, field
from typing import List, Optional

@dataclass
class GroupChat:
    name: str
    isChatGroup: bool = False
    following_admin: bool = False
    isActive: bool = False

    users_to_follow: list = field(default_factory=list)
    regex_text_to_follow: list = field(default_factory=list)

    to_https: str = None
    to_bot: str = None
    to_group: str = ''
    to_user: str = ''



groups_to_follow = [
    GroupChat(**val) for val in following_groups.values()
    if val.get('isActive') == True
]


@bp_telegram.route('/myinfo')
def myinfo():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = TelegramClient(StringSession(session_token), api_id, api_hash, loop=loop)
    client.start()

    me = client.get_me()
    print(me.stringify())
    return 'ok'

@bp_telegram.route('/get_messages')
def participants():

    to_notify = False
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = TelegramClient(StringSession(session_token), api_id, api_hash, loop=loop)
    client.start()

    limit_timedelta = datetime.now(timezone.utc) - timedelta(minutes=10)
    for group in groups_to_follow:
        chat = group.name
        messages_to_forward = [] ## final results
        if group.isChatGroup:
            admin_users = client.get_participants(chat, filter=ChannelParticipantsAdmins)

            users_filter = group.following_admin and admin_users or  [
                usr
                for usr in admin_users
                if usr.username in group.users_to_follow
            ]

            for user in users_filter:
                result = client(functions.messages.SearchRequest(
                    peer=chat,  # On which chat/conversation
                    q='',  # What to search for
                    filter=InputMessagesFilterEmpty(),  # Filter to use (maybe filter for media)
                    min_date=None,
                    # min_date=None,
                    max_date=None,  # Maximum date
                    offset_id=0,  # ID of the message to use as offset
                    add_offset=0,  # Additional offset
                    limit=500,  # How many results
                    max_id=0,  # Maximum message ID
                    min_id=0,  # Minimum message ID
                    from_id=user.id,  # Who must have sent the message (peer)
                    hash=0  # Special number to return nothing on no-change
                ))
                msg_result = [ msg for msg in result.messages if msg.date > limit_timedelta]

                messages_to_forward = messages_to_forward + msg_result


        messages_to_forward.sort(key=lambda x : x.id)

        print("new messages : " ,len(messages_to_forward))

        if messages_to_forward:
            notify = True
            client(functions.messages.ForwardMessagesRequest(
                from_peer=group.name,  # who sent these messages?
                id=[msg.id for msg in messages_to_forward],  # which are the messages?
                to_peer='phamhuonggfs_bot',  # who are we forwarding them to?,
                silent=True
            ))

    if to_notify:
        Bot(token=group.to_https).sendMessage(chat_id=group.to_user, text='got new message')

    return 'ok'