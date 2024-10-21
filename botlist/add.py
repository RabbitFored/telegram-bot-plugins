import datetime
import os
import tempfile

from pyrogram import Client, filters
from pyrogram.enums import ListenerTypes, MessageEntityType
from pyrogram.errors import UsernameInvalid
from pyrogram.types import InputMediaPhoto

from bot import logger
from bot.core.utils import generate_keyboard

from .db import add_bot, get_bot
from .preview import BotPreview
from .resize import extend_uniform_background


def get_tags(message):
    tags = []
    if message.entities:
        for entity in message.entities:
            if entity.type == MessageEntityType.HASHTAG:
                tag = message.text[entity.offset : entity.offset + entity.length]
                tags.append(tag)
    return tags


@Client.on_message(filters.command(["add", "new"]))
async def addTheBot(client, message):

    warn = """
**Before sumbitting the bot, make sure that your bot follows these rules:**
1) It should not contain any 18+ or other illegal contents.
2) Bots made with tools like manybots, livegram are not allowed.
3) No cloned bots should be submitted
4) Bots which promote illegal activities are not allowed

__Now send the username of the bot you want to suggest__
"""
    botid = await message.chat.ask(warn, reply_to_message_id=message.id)
    fetch_msg = await botid.reply_text("Fetching info...", quote=True)
    try:
        chat = await client.get_users(botid.text)
    except UsernameInvalid:
        return await fetch_msg.edit(
            "❌ Username invalid.\n\nSend your bot's username in the format: @mailableBot"
        )
    if not chat.is_bot:
        return await message.reply("This is not a bot.")
    botexist = bool(await get_bot(chat.id))
    if botexist:
        return await fetch_msg.edit_text(
            "❌ Sorry, This bot already exists in our archive."
        )

    Preview = BotPreview()
    Preview.id = chat.id
    Preview.title = chat.first_name
    Preview.username = chat.username
    Preview.pic = chat.photo.big_file_id if chat.photo else None
    # dev = await message.chat.ask("Send the developer's username", reply_markup=generate_keyboard("[Yes](data::yes) [No](data::no)"))
    # if dev.text == "yes":
    #    Preview.developer = ""
    with tempfile.TemporaryDirectory(prefix=f"{message.from_user.id}_") as temp_dir:
        if chat.photo:
            temp_file_path = os.path.join(temp_dir, "original.jpg")
            temp_out_file = os.path.join(temp_dir, "output.jpg")

            await client.download_media(
                chat.photo.big_file_id, file_name=temp_file_path
            )
            extend_uniform_background(temp_file_path, 2560, 1440, temp_out_file)
            await fetch_msg.delete()

            photo_path = temp_out_file
        else:
            photo_path = "public/assets/default_pic.jpg"

        post = await message.reply_photo(
            photo=photo_path,
            caption=Preview.get_caption(),
            reply_markup=Preview.get_keyboard(),
        )
    while True:
        try:
            media = None
            ask = await client.listen(
                message_id=post.id, listener_type=ListenerTypes.CALLBACK_QUERY
            )
            await ask.answer()

            if ask.data == "submit":
                botexist = bool(await get_bot(chat.id))
                if botexist:
                    return await fetch_msg.edit_text(
                        "❌ Sorry, This bot already exists in our archive."
                    )
                if Preview.ready():
                    data = {
                        "userid": chat.id,
                        "name": chat.first_name,
                        "username": chat.username,
                        "dc": chat.dc_id if chat.dc_id else 0,
                        "info": {
                            "about": {
                                "preview_img": post.photo.file_id,
                                "description": Preview.description,
                                "category": Preview.category,
                                "languages": Preview.languages,
                                "tags": Preview.tags
                                # developer = b['developer']
                            },
                            "features": {
                                "inline_support": Preview.inline_support,
                                "group_support": Preview.group_support,
                            },
                            "approval": {
                                "status": "pending",
                                "submitted_by": ask.from_user.id,
                                "submitted_on": datetime.datetime.now(),
                            },
                        },
                    }
                    await add_bot(data)
                    await client.send_photo(
                        -1002233681213,
                        photo=post.photo.file_id,
                        caption=Preview.get_caption(),
                        reply_markup=generate_keyboard(
                            f"[Approve ✅](data::approve_{Preview.id}_{ask.from_user.id})\n[Reject ❌](data::reject_{Preview.id}_{ask.from_user.id})"
                        ),
                        reply_to_message_id=32016,
                    )
                    return await ask.message.reply("submited successfully")
                else:
                    await message.reply("❌ Fill all fields to submit bot")
                await ask_it.sent_message.delete()
            elif ask.data == "ed_supg":
                t = "no" if Preview.group_support == "yes" else "yes"
                Preview.group_support = t
            elif ask.data == "ed_subc":
                t = "no" if Preview.inline_support == "yes" else "yes"
                Preview.inline_support = t
            elif ask.data == "ed_title":
                ask_it = await message.chat.ask(
                    "Send me a new title for the bot (max 30 characters)"
                )
                await ask_it.sent_message.delete()
                if not (len(ask_it.text)) < 30:
                    await ask_it.reply_text(
                        "Sorry, this isn't a proper title for a bot"
                    )
                    continue
                Preview.title = ask_it.text
            elif ask.data == "ed_pic":
                ask_it = await message.chat.ask("Now send me the new botpic")
                if ask_it.photo:
                    #                  if not
                    media = ask_it.photo.file_id
                    Preview.pic = ask_it.photo.file_id
                else:
                    await ask_it.reply(
                        "Please send me the picture as a 'Photo', not as a 'File'."
                    )
                await ask_it.sent_message.delete()
            elif ask.data == "ed_description":
                ask_it = await message.chat.ask(
                    "Send me the new description for the bot (min 30 and max 300 characters)"
                )
                if not 30 < (len(ask_it.text)) < 300:
                    await ask_it.reply_text(
                        "Sorry, this isn't a proper description for a bot"
                    )
                    continue
                Preview.description = ask_it.text
                await ask_it.sent_message.delete()
            elif ask.data == "ed_language":
                ask_it = await message.chat.ask(
                    'What language your bot supportsn\n Divide them using a space, ex. "Italian English Spanish"'
                )
                Preview.languages = ask_it.text
                await ask_it.sent_message.delete()
            elif ask.data == "ed_category":
                btn = """
[Art & Design 🎨](data::Art & Design) [Educational  📚](data::Educational)
[Entertainment 📚](data::Entertainment) [Finance 📊](data::Finance)
[Gaming 🎮](data::Gaming) [Multiuse 🧰](data::Multiuse)
[Music 🎧](data::Music) [Miscellaneous 🔀](data::Miscellaneous)
[News & Updates 📢](data::News & Updates)  [Travel & Photography 💬](data::Travel & Photography)
[Social 💬](data::Social) [Tools 🛠️](data::Tools)
[Others](data::Others)
                """
                ask = await message.reply_text(
                    "Select the category", reply_markup=generate_keyboard(btn)
                )
                ask_it = await client.listen(
                    message_id=ask.id, listener_type=ListenerTypes.CALLBACK_QUERY
                )
                await ask_it.answer()
                Preview.category = ask_it.data
                await ask.delete()
            elif ask.data == "ed_tags":
                ask_it = await message.chat.ask(
                    """Now send me some tags to define the bot and improve our search indexing, use # and divide them by a space. For ex. #converter #donwload #inline
You can use a maximum of 30 tags for 300 character"""
                )
                tags = get_tags(ask_it)
                Preview.tags = tags
                await ask_it.sent_message.delete()
            else:
                continue

            if media:
                await post.edit_media(
                    media=InputMediaPhoto(media, caption=Preview.get_caption()),
                    reply_markup=Preview.get_keyboard(),
                )
            else:
                await post.edit_caption(
                    caption=Preview.get_caption(), reply_markup=Preview.get_keyboard()
                )
        except Exception as e:
            logger.info(f"{e}")