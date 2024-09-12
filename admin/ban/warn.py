from pyrogram import Client, filters

from bot.core import database as db
from bot.core import filters as fltr
from bot.core import utils


@Client.on_message(fltr.cmd(["warn"])  & fltr.group("admin") )
async def warn(client, message):
  userID, username = utils.get_target_user(message)
  user = await db.get_user(userID, username, fetch_info=True)

  if not user:
      await message.reply_text("**No user found!**")
      return

  await user.warn()
  await message.reply_text(f"Warned {userID}")
    
@Client.on_message(fltr.cmd(["clear_warns"])  & fltr.group("admin") )
async def clear_warns(client, message):
  userID, username = utils.get_target_user(message)
  user = await db.get_user(userID, username, fetch_info=True)

  if not user:
      await message.reply_text("**No user found!**")
      return

  await user.clear_warns()
  await message.reply_text(f"Cleared all warnings for {userID}")
