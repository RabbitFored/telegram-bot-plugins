from pyrogram import Client

from bot.core import database as db
from bot.core import filters as fltr
from bot.core import utils


@Client.on_message(fltr.cmd(["ban"])  & fltr.group("admin") )
async def ban(client, message):
  userID, username = utils.get_target_user(message)
  user = await db.get_user(userID, username, fetch_info=True)

  if not user:
      await message.reply_text("**No user found!**")
      return

  await user.ban()
  await message.reply_text(f"Banned {userID}")

@Client.on_message(fltr.cmd(["unban"])  & fltr.group("admin") )
async def unban(client, message):
  userID, username = utils.get_target_user(message)
  user = await db.get_user(userID, username, fetch_info=True)

  if not user:
      await message.reply_text("**No user found!**")
      return

  await user.unban()
  await message.reply_text(f"Unbanned {userID}")

