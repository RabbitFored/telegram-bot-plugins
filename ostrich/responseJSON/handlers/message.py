
from pyrogram import Client, filters
from bot.core import utils

@Client.on_message(filters.private)
async def msg_handler(client, message):
    me = await client.get_me()
    if bool(message.via_bot) and message.via_bot.id == me.id:
       return
    json_objects = utils.chunkstring(str(message), 4000)
    for json_object in json_objects:
        await message.reply_text(
          f'''
          ```json
          {json_object}
          ```
          ''',
          disable_web_page_preview=True,
          disable_notification=True,
        )
