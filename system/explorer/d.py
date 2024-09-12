'''
from pyrogram import Client, filters
import urllib.parse
from bot.core import database as db
from bot.core import filters as fltr


from bot.core.utils import generate_keyboard
from pyrogram.enums import ListenerTypes
import time
from bot import web
from quart import Quart, send_file, abort

baseURL = os.environ['baseURL']


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

'''




