from pyrogram import Client, filters
from bot.core.utils import generate_keyboard, check_sub
import os 
from bot import strings


@Client.on_message(filters.private , group=-10)
async def force_sub(client, message):
    userID = message.from_user.id
    chat = os.environ.get("FORCE_SUB_CHAT", None)
    if chat:
      is_subscribed = await check_sub(client, chat, userID, ignore_error=True)
      if is_subscribed:
        message.continue_propagation()
      else:
        chat_info = await client.get_chat(chat)
        invite_link = chat_info.invite_link or f"https://t.me/{chat_info.username}"
        text = strings.get("force_sub_txt",
                           channel=f"{'@'+chat_info.username if chat_info.username else chat_info.title}")
        keyboard = generate_keyboard(
          strings.get("force_sub_btn", channel_url=invite_link))
        await message.reply(
          text,
          disable_web_page_preview=True,
          reply_markup=keyboard,
          quote=True,
        )
        message.stop_propagation()
