from pyrogram import Client

from bot.core import database as db
from bot.core import filters as fltr
from bot.core import utils
#import speedtest

@Client.on_message(fltr.cmd(["speedtest"])  & fltr.group("admin") )
async def speedtest(client, message):
        pass