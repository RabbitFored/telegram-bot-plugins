import os

import requests
from pyrogram import Client, filters
from pyrogram.enums import ListenerTypes, MessageEntityType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.core import database as db


@Client.on_message(filters.command(["send"]))
async def send_mail(client, message):

    user = await db.get_user(message.from_user.id)

    if user.subscription["name"] == "free":
        await message.reply(
            "You discovered a premium feature. Use /premium to upgrade your account."
        )
        return

    mailIDs = user.data.get("mails", [])

    sendable_domains = ["mail.bruva.co", "4qnt.us"]

    usable_mails = []

    for mailID in mailIDs:
        id, domain = mailID.split("@")
        if domain in sendable_domains:
            usable_mails.append(mailID)

    if len(usable_mails) == 0:
        await message.reply(
            "You dont have any mail which can perform this action. Use /generate to get a new mail."
        )
        return

    buttons = []

    for mail in usable_mails:
        buttons.append([InlineKeyboardButton(mail, mail)])

    ask_mail = await message.chat.ask(
        "**Select a mail:**",
        reply_markup=InlineKeyboardMarkup(buttons),
        listener_type=ListenerTypes.CALLBACK_QUERY,
    )

    if ask_mail.message.id != ask_mail.sent_message.id:
        await message.reply("Callback query intreption. Try again")
        return

    mailID = ask_mail.data

    id, domain = mailID.split("@")

    await ask_mail.message.delete()

    ask_recipient = await message.chat.ask("**Send me recipient mail**")
    to = []
    for entity in ask_recipient.text.entities:
        if entity.type == MessageEntityType.EMAIL:
            o = entity.offset
            l = entity.length
            recipient = ask_recipient.text[o : o + l]
            id, d = recipient.split("@")
            sp = d.split(".")
            if "gov" in sp or id == "gov":
                await message.reply("Cannot send mail to this ID. Forbidden action")
                return
            to.append(recipient)

    if len(to) == 0:
        await ask_recipient.reply(
            "**Please provide a valid mail./nUse /send to redo this task.**"
        )
        return

    subject = await message.chat.ask("Provide mail subject")
    body = await message.chat.ask("Send any text to send.")

    mailgun_api = f"https://api.mailgun.net/v3/{domain}/messages"
    mailgun_token = os.environ.get("mailgun_token", "")

    r = requests.post(
        mailgun_api,
        auth=("api", mailgun_token),
        data={"from": mailID, "to": to, "subject": subject.text, "text": body.text},
    )

    if r.status_code == 200:
        await body.reply(
            "**Mail sent successfully.**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Get Help", url="https://telegram.dog/ostrichdiscussion"
                        ),
                    ]
                ]
            ),
        )
        await db.inc_stat("sent", 1)
    else:
        await body.reply(
            "**Something went wrong, contact support**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Get Help", url="https://telegram.dog/ostrichdiscussion"
                        ),
                    ]
                ]
            ),
        )
