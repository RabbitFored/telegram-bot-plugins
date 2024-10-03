from pyrogram import Client, filters
import os
from bot.core import database as db
from bot.core import filters as fltr
import time
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

PRGRS = {}

def humanbytes(size):
    if not size:
        return ""
    power = 2 ** 10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
          ((str(hours) + "h, ") if hours else "") + \
          ((str(minutes) + "m, ") if minutes else "") + \
          ((str(seconds) + "s, ") if seconds else "") + \
          ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]

async def progress_func(
    current,
    total,
    ud_type,
    message,
    start
):
  now = time.time()
  diff = now - start
  if round(diff % 5.00) == 0 or current == total:
    percentage = current * 100 / total
    speed = current / diff
    af = total / speed
    elapsed_time = round(af) * 1000
    time_to_completion = round((total - current) / speed) * 1000
    estimated_total_time = elapsed_time + time_to_completion
    eta =  TimeFormatter(milliseconds=time_to_completion)
    elapsed_time = TimeFormatter(milliseconds=elapsed_time)
    estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

    PRGRS[f"{message.chat.id}_{message.id}"] = {
        "current": humanbytes(current),
        "total": humanbytes(total),
        "speed": humanbytes(speed),
        "progress": percentage,
        "eta": eta
    }

@Client.on_callback_query(fltr.on_data("progress_msg"))
async def cb_handler(client, query):

              try:
                  msg = "Progress Details...\n\nCompleted : {current}\nTotal Size : {total}\nSpeed : {speed}\nProgress : {progress:.2f}%\nETA: {eta}"
                  await query.answer(
                      msg.format(
                          **PRGRS[f"{query.message.chat.id}_{query.message.id}"]
                      ),
                      show_alert=True
                  )

              except:
                  await query.answer(
                      "Processing your file...",
                      show_alert=True
                  )

@Client.on_message(filters.command(["save", "dl"]))
async def dl(client, message):
     user = await db.get_user(message.from_user.id)
     shared_path = user.data.get("shared_path", "/shared/jelly/downloads")
    
     msg = await client.send_message(chat_id=message.chat.id, text=f'**Downloading your file to {shared_path}...**',reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Check Progress", callback_data="progress_msg")]
    ]))
     c_time = time.time()
     media = message.reply_to_message
     await media.download(shared_path, progress=progress_func, progress_args=(
                               "**Downloading your file to server...**",
                               msg,
                               c_time))

@Client.on_message(filters.command(["set"]))
async def set(client, message):
     user = await db.get_user(message.from_user.id)
 
     ask_path = await message.chat.ask("Send me path")
     await user.data.set({"shared_path": ask_path.text})
     await message.reply("Path set successfully")
    
@Client.on_message(filters.command(["get_path"]))
async def get_path(client, message):
     user = await db.get_user(message.from_user.id)
     p = user.data.get("shared_path", "/shared/jelly/downloads")
     await message.reply(p)