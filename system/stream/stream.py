import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
from quart import send_file

from bot import web


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

@web.route('/download/<token>')
async def download_d(token):
    path = decrypt_path(token)
    return await send_file(path, as_attachment=True)