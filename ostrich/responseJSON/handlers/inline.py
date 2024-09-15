from pyrogram import Client
from bot.core import utils
from pyrogram.types import (InlineQueryResultArticle, InputTextMessageContent,
InlineKeyboardMarkup, InlineKeyboardButton)

@Client.on_chosen_inline_result()
async def inline_result(client, inline_query):
    json_objects = utils.chunkstring(str(inline_query), 4000)
    for json_object in json_objects:
        await client.send_message(
          chat_id=inline_query.from_user.id,
          text = f'''
          ```json
          {json_object}
          ```
          ''',
          disable_web_page_preview=True,
          disable_notification=True,
        )



@Client.on_inline_query()
async def inline_query(client, inline_query):
      await inline_query.answer(results=[
        InlineQueryResultArticle(title="JSON response",
                                 input_message_content=InputTextMessageContent(
                                       f'''
                                       ```json
                                       {inline_query}
                                       ```
                                       '''),
                                 description="@responseJSONbot",
                                 thumb_url="https://i.imgur.com/JyxrStE.png"),
        InlineQueryResultArticle(
          title="About",
          input_message_content=InputTextMessageContent(
            "**Response JSON BOT - @ theostrich**"),
          url="https://t.me/theostrich",
          description="About bot",
          thumb_url="https://imgur.com/DBwZ2y9.png",
          reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Updates", url="https://t.me/ostrichdiscussion")
          ]])),
      ])


