import os
import time

from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.core import filters as fltr
from bot.core.utils import generate_keyboard, progress_func


async def list_dir(_, m, path):
  dir_list = os.listdir(path)

  btn = "[..](data::back)\n"
  for i in dir_list:
    btn += f"[{i}](data::ch_{dir_list.index(i)})\n"
  if m.from_user.is_self:
    await m.edit_text(path, reply_markup=generate_keyboard(btn))
  else:
    await m.reply(path, reply_markup=generate_keyboard(btn))

async def file_options(client, message, target_file):
  btn = "[Upload 📤](data::upload) [Stream 📺](data::stream)\n[Rename ✏️](data::rename) [Delete 🗑️](data::delete)\n[Back](data::back)"
  if message.from_user.is_self:
    await message.edit_text(target_file, reply_markup=generate_keyboard(btn))
  else:
    await message.reply(target_file, reply_markup=generate_keyboard(btn))


@Client.on_message(fltr.cmd(["ls"]) & fltr.group("admin") )
async def ls(client, message):
  path = os.getcwd()
  await list_dir(client, message, path)

@Client.on_callback_query(fltr.on_marker("ch"))
async def change_dir(client, query):
  data = query.data.split("_")
  target = data[1]
  dir_list = os.listdir(query.message.text)
  target_path = os.path.join(query.message.text, dir_list[int(target)])
  if os.path.isfile(target_path):
    await file_options(client, query.message, target_path)
  else:
    await list_dir(client, query.message, target_path)


@Client.on_callback_query(fltr.on_data("upload"))
async def upload(client, query):
  path = query.message.text
  if not os.path.exists(path):
    await query.answer(
      "File not found!",
      show_alert=True
    )
    return
  msg = await query.message.reply(
    text='**Uploading your file to my server...**',
    reply_markup=InlineKeyboardMarkup([[
        InlineKeyboardButton(text="Check Progress",
                             callback_data="progress_msg")
    ]]))
  try:
    c_time = time.time()
    await query.message.reply_document(
      query.message.text,
      reply_to_message_id=query.message.id,
      progress=progress_func,
      progress_args=("**Uploading your file to server...**", msg, c_time))
  except ValueError as e:
    await query.answer(f"❌ Error: {e}", show_alert=True)
  await msg.delete()
  
@Client.on_callback_query(fltr.on_data("delete"))
async def delete(client, query):
  path = query.message.text
  if not os.path.exists(path):
    await query.answer(
      "File not found!",
      show_alert=True
    )
    return
  os.remove(query.message.text)
  await query.answer("File deleted successfully!")

@Client.on_callback_query(fltr.on_data("rename"))
async def rename(client, query):
  old_path = query.message.text
  if not os.path.exists(old_path):
    await query.answer(
      "File not found!",
      show_alert=True
    )
    return
  parent_dir = os.path.dirname(query.message.text)
  new_file_name = await query.message.ask("send new file name")
  new_path = os.path.join(parent_dir, new_file_name.text)
  os.rename(old_path, new_path)

  await query.answer("File renamed successfully!")
  await file_options(client, query.message, new_path)

@Client.on_callback_query(fltr.on_data("back"))
async def back(client, query):
  if query.message.text == "/":
    await query.answer("Cannot go back, You are at the root directory!")
    return
  path = os.path.dirname(query.message.text)
  await list_dir(client, query.message, path)

'''
@Client.on_callback_query(fltr.on_data("stream"))
async def stream(client, query):
  baseURL = os.environ['baseURL']
  path = query.message.text
  if not os.path.exists(path):
    await query.answer(
      "File not found!",
      show_alert=True
    )
    return
  
  secret_token = encrypt_path(path)
  url = urllib.parse.urljoin(baseURL, "/download/" + secret_token)
  await query.message.reply(url,reply_markup=generate_keyboard(f"[OPEN](url::{url})"))
'''
