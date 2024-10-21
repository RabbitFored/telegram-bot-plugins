from pyrogram import Client
from pyrogram.errors import ChatAdminRequired, UserNotParticipant

from bot import logger
from bot.core import filters as fltr

from .db import get_bot, rate
from .preview import BotPreview


def calculate_average_rating(ratings):
    print(ratings)
    total_users = len(ratings)
    total_ratings = 0
    for user, rating in ratings.items():
        total_ratings += int(rating)

    average_rating = total_ratings / total_users
    return round(average_rating, 1)


@Client.on_callback_query(fltr.on_marker("rt"))
async def rate_bot(client, query):
    userid = query.from_user.id
    chatid = query.message.chat.id
    c = -1001475798954
    message = query.message
    messageId = query.message.id
    data = query.data
    rating = data.split("_")[1]
    botid = data.split("_")[2]

    try:
        await client.get_chat_member(chatid, userid)
    except UserNotParticipant:
        return await query.answer(
            "❌ Join the channel to vote this bot", show_alert=True
        )
    except ChatAdminRequired:
        logger.error("Chat Admin Permission Required to perform this function")
        return
    await rate(userid, rating, botid)
    await query.answer(f"You rated: {rating}")

    b = await get_bot(botid)
    Preview = BotPreview()
    Preview.id = b["userid"]
    Preview.title = b["name"]
    Preview.username = b["username"]
    Preview.description = b["info"]["about"]["description"]
    Preview.rating = calculate_average_rating(b["ratings"])
    Preview.votes = len(b["ratings"])
    Preview.category = b["info"]["about"]["category"]
    Preview.language = b["info"]["about"]["languages"]
    Preview.inline_support = b["info"]["features"]["inline_support"]
    Preview.group_support = b["info"]["features"]["group_support"]
    Preview.tags = b["info"]["about"]["tags"]

    await message.edit_caption(
        caption=Preview.get_caption(), reply_markup=message.reply_markup
    )
