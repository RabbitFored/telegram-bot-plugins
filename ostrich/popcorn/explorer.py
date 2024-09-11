from pyrogram import Client, filters
import urllib.parse
from bot.core import database as db
from bot.core import filters as fltr
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from bot.core.utils import generate_keyboard
from pyrogram.enums import ListenerTypes
from .dl import progress_func
import time
from bot import web, logger
from quart import Quart, send_file, abort
baseURL = os.environ['baseURL']

@Client.on_message(filters.command(["ls", "files"]))
async def ls(client, message):
  path = os.getcwd()
  await lsP(client, message, path)


async def lsP(client, message, path):

  dir_list = os.listdir(path)
  logger.info(f"{dir_list}")

  btn = "[..](data::back)\n"
  for i in dir_list:
    btn += f"[{i}](data::ch_{dir_list.index(i)})\n"
  if message.from_user.is_self:
    msg = await message.edit_text(path, reply_markup=generate_keyboard(btn))
  else:
    msg = await message.reply(path, reply_markup=generate_keyboard(btn))
  #ask = await client.listen(
  # message_id=msg.id, listener_type=ListenerTypes.CALLBACK_QUERY)


@Client.on_callback_query(fltr.on_marker("ch"))
async def c_handler(client, query):
  data = query.data.split("_")
  target = data[1]
  dir_list = os.listdir(query.message.text)
  target_path = os.path.join(query.message.text, dir_list[int(target)])
  if os.path.isfile(target_path):
    await file_i(client, query.message, target_path)
  else:
    await lsP(client, query.message, target_path)

async def file_i(client, message, target_file):
    btn = "[Upload 📤](data::upload) [Stream 📺](data::stream)\n[Rename ✏️](data::rename) [Delete 🗑️](data::delete)\n[Back](data::back)"
    if message.from_user.is_self:
      msg = await message.edit_text(target_file, reply_markup=generate_keyboard(btn))
    else:
      msg = await message.reply(target_file, reply_markup=generate_keyboard(btn))


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
  except ValueError as ve:
    await query.answer(f"❌ Error: {ve}", show_alert=True)
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
  await file_i(client, query.message, new_path)

@Client.on_callback_query(fltr.on_data("stream"))
async def stream(client, query):
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


@Client.on_callback_query(fltr.on_data("back"))
async def back(client, query):
  if query.message.text == "/":
    await query.answer("Cannot go back, You are at the root directory!")
    return
  path = os.path.dirname(query.message.text)
  await lsP(client, query.message, path)

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import os

SECRET_KEY = os.environ.get("key", "7F30F2253DEC8C1E88D3C0C91416AE1B").encode('utf-8')

def encrypt_path(file_path):
  iv = os.urandom(16)  # Generate a secure random IV
  cipher = Cipher(algorithms.AES(SECRET_KEY), modes.CFB(iv), backend=default_backend())
  encryptor = cipher.encryptor()
  encrypted_path = iv + encryptor.update(file_path.encode()) + encryptor.finalize()

  # Base64 encode and remove trailing padding "="
  return base64.urlsafe_b64encode(encrypted_path).rstrip(b'=').decode()

def decrypt_path(encrypted_token):
  # Add padding if needed
  missing_padding = len(encrypted_token) % 4
  if missing_padding:
      encrypted_token += '=' * (4 - missing_padding)

  # Decode the base64 encoded string
  encrypted_path = base64.urlsafe_b64decode(encrypted_token.encode())
  iv = encrypted_path[:16]  # Extract the IV from the beginning of the ciphertext
  cipher = Cipher(algorithms.AES(SECRET_KEY), modes.CFB(iv), backend=default_backend())
  decryptor = cipher.decryptor()

  # Decrypt the path using the extracted IV
  decrypted_path = decryptor.update(encrypted_path[16:]) + decryptor.finalize()
  return decrypted_path.decode()

@web.route('/download/<token>')
async def download(token):
    path = decrypt_path(token)
    return await send_file(path, as_attachment=True)