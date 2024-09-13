import base64
import os
import time
import urllib.parse

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.core import filters as fltr
from bot.core.utils import generate_keyboard, progress_func

from ..stream import encrypt_path


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


SECRET_KEY = os.environ.get("key", "7F30F2253DEC8C1E88D3C0C91416AE1B").encode('utf-8')

def encrypt_path(file_path):
  iv = os.urandom(16)
  cipher = Cipher(algorithms.AES(SECRET_KEY), modes.CFB(iv), backend=default_backend())
  encryptor = cipher.encryptor()
  encrypted_path = iv + encryptor.update(file_path.encode()) + encryptor.finalize()
  return base64.urlsafe_b64encode(encrypted_path).rstrip(b'=').decode()

def decrypt_path(encrypted_token):
  missing_padding = len(encrypted_token) % 4
  if missing_padding:
      encrypted_token += '=' * (4 - missing_padding)
  encrypted_path = base64.urlsafe_b64decode(encrypted_token.encode())
  iv = encrypted_path[:16]
  cipher = Cipher(algorithms.AES(SECRET_KEY), modes.CFB(iv), backend=default_backend())
  decryptor = cipher.decryptor()
  decrypted_path = decryptor.update(encrypted_path[16:]) + decryptor.finalize()
  return decrypted_path.decode()


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


