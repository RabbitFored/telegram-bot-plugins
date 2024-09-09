from pyrogram import Client, filters

from bot.core import database as db


@Client.on_message(filters.command(["whois"]))
async def whois(client, message):
    args = message.text.split(" ")
    mailID = args[1]
    user = await db.find_user({"mails": mailID})
    await message.reply_text(f"Mail {mailID} belongs to `{user.ID}`")
