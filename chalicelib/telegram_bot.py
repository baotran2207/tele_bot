import os
import yaml
from pprint import pprint
from telethon import TelegramClient, events, sync
from telethon.sessions import StringSession
from telegram import Bot
from telethon import functions, types
from telethon.tl.types import \
    ChannelParticipantsAdmins, ChannelParticipantCreator, ChannelParticipantAdmin, \
    PeerUser, PeerChat, PeerChannel

from telethon.tl.functions.channels import GetParticipantRequest

import telethon.tl.functions as functions

from dataclasses import dataclass, asdict, field
from typing import List, Optional
# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.

################################################################
##Hard coded##
################################################################
api_id = "9711628"
api_hash = "8f1ec08e24017ff5a1498dfd08746549"
# session_token = "1BVtsOJ8Bu6wZYxN13ILphNLZbcFwu1QWO98gkYIOhMB456hQ6EeRkVgv1FDKEY_WJstffwh2CFdnl9mNCmDu4ycGaJ0JwTfcQKIpCw4wHm7SpVlwScQ-zlsdPAXJkt3gZenLa4ZFf4_syoRD4UFOCNBeSWRuuKYW7rNBN9UZ6oJ0KcTEBB99F-6nJbdDZ228u0xlW9xr-56CaHUjl1fzhM0vTOuXtL-11pqHpz62KYXk9KIoO1CJwQsdiFXihtw9ZIEyKoE4h4SNxwhp0i_ZZNGbaShZrX_m9hhdfNo2Azr05eeALxUiaSMvNvpaJu1OE6o3yUonPPauxyrOeXUL_zwzFIJ2bVc="
session_token = "1BVtsOJ8BuyrFpedSWLqIZ9Gl7kIWnSDOc0Yz_gL6zBP4EWvGR9yC2kLA01KFeIbnvuHG_Os3Lwo2nbt3hWS_OVz6kfwexhZodOXQTETm1NxZcWFSoHHN6G8ECEvzZig5e76sri8tNBNdg4oAtoiUyEDgPejY7JAqKvzt49M7R7H9Gqwlx-HifpXuqT3H1S2STWB6snjvQW4KuUFtemn1RkHtTVb4MHwdQ33AC43ws_nWSato_z-fE3uhCJKGkP4ArQHKWp5d9MuaB31ZZ2ZKNAXjSqJjwGRbQLYJrWlcf8P6py25QszOVWHsq1ed-POOr9AbPCU-fJAEUaWv2OjE_RODNCDl7OM="



bot_name_tester = "StagingTesterBot"
bot_token_tester = "5074060436:AAGgvV5ae3-IDvl8XwHiVbBJNVYCHgWf6ew"

test_group_id = 653082908
prod_group_id= 5074808760


bot_name_prod = "baotrancoin_bot"
bot_token_prod = "5074808760:AAHaoz00mwyL0XY7pXfuUEu_6ZVgCInqYkY"

bot_name_gfs = "phamhuonggfs_bot"


my_phone = "+84902866135"
my_id = 1501704566


# bot_username = bot_name_tester
# bot_token = bot_token_tester

bot_username= bot_name_prod
bot_token= bot_token_prod


################################################################
##Load chats definition##
################################################################
with open(
    os.path.join(os.path.dirname(__file__),'following_groups.yaml',
    ), 'r') as f:
    following_groups = yaml.load(f,  Loader=yaml.FullLoader)


@dataclass
class Botter:
    bot_token: str
    bot_username: str

    bot: Bot = None

    def send_message(self, receiver_id, text, **kwargs):
        self.bot.sendMessage(chat_id=receiver_id, text=text)

    def init_bot(self):
        print(self.bot_token)
        self.bot = Bot(self.bot_token)


@dataclass
class Chat:
    chat_name: str
    chat_id: str = ""
    following_username: list = field(default_factory=list)
    following_text: list = field(default_factory=list)
    following_users: list = field(default_factory=list)

@dataclass
class TeleUser:
    user_id : int
    username : str
    following : bool = False


@dataclass
class GroupChat:
    id: int
    name: str
    users_to_follow: List[TeleUser]

    isChatGroup: bool = False
    following_admin: bool = False
    isActive: bool = False
    regex_text_to_follow: list = field(default_factory=list)

    to_https: str = None
    to_bot: str = None
    to_group: int = None
    to_user: int = None

    def __post_init__(self):
        res = [ TeleUser(**user) for user in self.users_to_follow]
        self.users_to_follow = res

# bot = Botter(bot_token=bot_token, bot_username=bot_username)
# bot.init_bot()



##################
# Connect to client######
##################

def get_client():
    with TelegramClient(StringSession(session_token), api_id, api_hash) as client:
        return client

client = get_client()

client.start()
##################
# Get admin if not define######
##################
print('2.Get admin if not define')
def get_admins(chat):
    res = []
    for user in client.iter_participants(
        chat.name,
        filter=ChannelParticipantsAdmins
    ):
        print(f"- user_id: {user.id}")
        print(f"  username: '{user.username}'")
        print(f"  following: False")
        res.append(user)

    return res

groups_to_follow = [
    GroupChat(**val) for val in following_groups.values()
    if val.get('isActive') == True
]

for chat in groups_to_follow:
    print(f'---- {chat.name}')
    if not chat.users_to_follow:
        print(chat.name)
        admins = get_admins(chat)
        print(f"1. Admins for : {chat}")
        pprint(admins)

############
# New Message#
############


print('3.Message handler')


following_users_by_chat_id = {
    chat.id : [
        user for user in chat.users_to_follow
        # if user.following == True
        if not ('bot' in user.username) and user.following == True
    ]
    for chat in groups_to_follow
}

foward_to_by_chat_id = {
    chat.id: chat.to_group
    for chat in groups_to_follow
}


pprint(following_users_by_chat_id)


@client.on(
    events.NewMessage
)
async def handler(event):

    chat_from = event.chat if event.chat else (await event.get_chat())
    sender = await event.get_sender()

    chat_id = chat_from.id
    chat_title = chat_from.title if hasattr(chat_from, 'title' ) else 'No title'

    from_id = sender.id
    from_username = sender.username

    message = event.message.message
    message_id = event.message.id

    if sender.is_self:
        forward_to = PeerChat(test_group_id)
        print('----------------------from myself')
        print(
            event
        )
        print('forward_to ', forward_to)
        await client.forward_messages(
            forward_to,  # to which entity you are forwarding the messages
            event.message  # the IDs of the messages (or message) to forward
        )


    "A. filter out following group ! this section for testing"

    if chat_id not in following_users_by_chat_id.keys():
        ### not in prod yet
        print('----------------------not following ! chat_id from_id message : ', chat_id, from_id, message)

        return
    print(f'+++++++++ following {chat_title} ++ {from_username} : {message}')

    following_users  = following_users_by_chat_id.get(chat_id)

    following_user = [user for user in following_users if from_id == user.user_id]

    "B. Filter users to follow"

    if following_user:
        user = following_user[0]


        print(f'+++++++++ following {chat_title} ++ {from_username} : {message}')
        forward_to = PeerChat(
            foward_to_by_chat_id.get(chat_id)
        )

        if forward_to:
            print('    user ', user , user.following , type(user.following))
            await client.forward_messages(
                forward_to,  # to which entity you are forwarding the messages
                event.message,  # the IDs of the messages (or message) to forward
            )



        msg = f'+ {chat_title} - {from_username} :  {message}'
        print('notify', msg, user)
        # bot.sendMessage(
        #     chat_id=my_id,
        #     text=msg,
        # )


client.run_until_disconnected()
