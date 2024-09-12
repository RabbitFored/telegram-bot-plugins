from pyrogram import Client, filters

from bot.core import database as db
from bot.core import filters as fltr
from bot.core import utils


@Client.on_message(filters.private , group=-11)
async def check_ban(client, message):
    userID = message.from_user.id
    user = await db.get_user(userID)

    if bool(user.is_banned):
        await message.reply("You are banned from using this bot.")
        message.stop_propagation()