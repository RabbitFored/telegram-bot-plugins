from pyrogram import Client

from bot.core import filters as fltr
from bot.core.utils import generate_keyboard

from .db import approve_bot, publish_bot, reject_bot


@Client.on_callback_query(fltr.on_marker("approve"))
async def approve(client, query):
    data = query.data.split("_")
    botid = data[1]
    userid = data[2]
    verified_by = query.from_user.id
    await approve_bot(botid, verified_by)
    await query.answer("Approved success")
    message = query.message
    await message.edit_caption(
        caption=message.caption,
        caption_entities=message.caption_entities,
        reply_markup=generate_keyboard(f"[Publish](data::publish_{botid})"),
    )
    await client.send_message(
        userid, "Your request for adding this bot has been accepted by the admins"
    )


@Client.on_callback_query(fltr.on_marker("publish"))
async def publish(client, query):
    data = query.data.split("_")
    botid = data[1]
    message = query.message
    post = await client.send_photo(
        "GramBotList",
        photo=message.photo.file_id,
        caption=message.caption,
        caption_entities=message.caption_entities,
        reply_markup=generate_keyboard(
            f"[1⭐️](data::rt_1_{botid}) [2⭐️](data::rt_2_{botid}) [3⭐️](data::rt_3_{botid})\n[4⭐️](data::rt_4_{botid}) [5⭐️](data::rt_5_{botid})"
        ),
    )
    await publish_bot(botid, post.id)
    await query.answer("Published successfully")


@Client.on_callback_query(fltr.on_marker("reject"))
async def reject(client, query):
    data = query.data.split("_")
    botid = data[1]
    userid = data[2]
    verified_by = query.from_user.id
    await reject_bot(botid, verified_by)
    await client.send_message(
        userid, "Your request for adding this bot has been rejected by the admins"
    )
