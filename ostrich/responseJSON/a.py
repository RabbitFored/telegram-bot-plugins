from pyrogram import Client, filters
from bot.core.utils import generate_keyboard
from pyrogram.types import ReplyKeyboardMarkup


@Client.on_message(filters.command(["inline_button"]))
async def get_inline_button(client, message):
    text = "**Sample Inline buttons:**"
    btn = '''[Button 1](data::Never) [Button 2](data::Gonna)
                  [Button 3](data::Give) [Button 4](data::You)
                  [Button 6](data::Up)'''
    keyboard = generate_keyboard(btn)
    await message.reply_text(
        text,
        disable_web_page_preview=True,
        reply_markup=keyboard,
        quote=True,
    )


@Client.on_message(filters.command(["reply_button"]))
async def get_reply_button(client, message):
    text = "**Sample ReplyKeyboardMarkup buttons:**"
    await message.reply_text(
        text,
        disable_web_page_preview=True,
         reply_markup=ReplyKeyboardMarkup(
            [
                ["A", "B", "C"], 
                ["D", "E"],
                ["hello world"]
            ],
            resize_keyboard=True
        ),
        quote=True,
    )