from pyrogram import Client, filters

from bot.core import database as db
from bot.core import filters as fltr
from bot.core import utils


@Client.on_message(fltr.cmd(["warn"])  & fltr.group("admin") )
async def word_count(client, message):
  pass