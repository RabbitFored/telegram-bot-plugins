from pyrogram import Client, filters
from pyrogram.enums import ListenerTypes, MessageEntityType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import os
from bot import strings
from bot.core import database as db
from bot.core import utils
from bot.core.utils import gen_rand_string, generate_keyboard


async def no_mails(message):
    text = strings.get("no_mails_txt")
    await message.reply_text(text, quote=True)


@Client.on_message(filters.command(["mails", "transfer", "delete"]))
async def mail_action(client, message):
    user = await db.get_user(message.from_user.id)
    mailIDs = user.data.get("mails", [])

    command = message.text.split(" ")[0][1:]
    actions = {"mails": "info", "transfer": "tr", "delete": "dl"}

    r = "m"

    if len(mailIDs) == 0:
        await no_mails(message)
        return
    text = strings.get("select_mail_txt")
    btns = ""

    for mailID in mailIDs:
        btn = strings.get(
            "select_mail_btn", mailID=mailID, action=actions[command], r=r
        )
        btns += f"{btn}\n"
    keyboard = generate_keyboard(btns)
    await message.reply_text(text, reply_markup=keyboard, quote=True)


@Client.on_message(filters.command(["generate"]))
async def generate(client, message):
    user = await db.get_user(message.from_user.id)

    mailIDs = user.data.get("mails", [])
    limits = user.get_limits()

    if len(mailIDs) >= limits["max_mails"]:
        await message.reply(
            f"**Your plan includes reserving {limits['max_mails']} mails only.\nSwitch to premium plan to make more mails.**"
        )
        return

    domains = os.environ('domains')

    if user.subscription["name"] == "premium":
        user_domains = user.data.get("domains", [])
        domains = domains + user_domains

    buttons = []
    for domain in domains:
        buttons.append([InlineKeyboardButton(domain, f"{domain}")])

    ask_dom = await message.chat.ask(
        "**Select a domain:**",
        reply_markup=InlineKeyboardMarkup(buttons),
        listener_type=ListenerTypes.CALLBACK_QUERY,
    )
    if not ask_dom.message.id == ask_dom.sent_message.id:
        await message.reply("Callback query intreption. Try again")
        return
    domain = ask_dom.data

    if domain not in domains:
        await message.reply("**Invalid domain.**")
        return

    mailID = gen_rand_string(8).lower() + "@" + domain

    await user.data.addToSet({"mails": mailID})
    await db.inc_stat("mails", 1)

    await ask_dom.message.reply_text(
        f"Mail Created successfully.\nYour mail id : {mailID}\nNow You can access your mails here."
    )


@Client.on_message(filters.command(["set"]))
async def set_mail(client, message):
    user = await db.get_user(message.from_user.id)
    mailIDs = user.data.get("mails", [])
    limits = user.get_limits()

    if len(mailIDs) >= limits["max_mails"]:
        await message.reply(
            f"**Your plan includes reserving {limits['max_mails']} mails only.\nSwitch to premium plan to make more mails.**"
        )
        return

    mailID = None
    for entity in message.entities:
        if entity.type == MessageEntityType.EMAIL:
            o = entity.offset
            l = entity.length
            mailID = message.text[o : o + l]
    if mailID == None:
        await message.reply_text(text="**Provide a valid mail ID.**")
        return

    domains = os.environ('domains')
    if user.subscription["name"] == "premium":
        user_domains = user.data.get("domains", [])
        domains = domains + user_domains

    reserved_keyword = os.environ('reserved_keyword')

    id, domain = mailID.split("@")

    if id in reserved_keyword:
        await client.send_message(
            message.chat.id, f"**Sorry this mail ID is unavailable**"
        )
        return

    if domain not in domains:
        await client.send_message(
            message.chat.id,
            f"**The domain {domain} is not maintained by us.\nUse /domains to check list of available domains.\n\nIf you are the owner of {domain} and interested to use it in this bot, contact us at @ostrichdiscussion.**",
        )
        return

    dataExists = await db.data_exists({"mails": mailID})
    if dataExists:
        await client.send_message(message.chat.id, "Sorry this mail ID is unavailable")
        return
    await user.data.addToSet({"mails": mailID})
    await db.inc_stat("mails", 1)
    await message.reply_text(
        f"Mail Created successfully.\nYour mail id : {mailID}\nNow You can access your mails here."
    )


async def transfer_mail(client, message, mail):
    id, domain = mail.split("@")
    domains = os.environ('domains')
    if domain not in domains:
        await message.chat.ask("**Cannot transfer this mail**")
        return
    recipient = await message.chat.ask("**Please enter new owners username**")
    userid2, username2 = utils.get_target_user(recipient)
    t = userid2 or username2

    user2 = await db.get_user(userid2, username2)

    args = recipient.text.split(" ")

    if not userid2 and not username2:
        await message.reply_text(
            "**Provide a valid Username. Use /transfer to restart this process**"
        )
        return
    if not user2:
        return await message.reply_text(
            f"**Cannot transfer {mail} to {args[0]}.\nBe sure that the user started me.**"
        )
    try:
        await client.send_message(
            args[0],
            f"**Incoming mail transfer request for {mail} by {message.reply_to_message.from_user.mention()}**",
        )
    except:
        await message.reply_text(
            f"**Cannot transfer {mail} to {args[0]}.\nBe sure that the user started me.**"
        )
        return

    user1 = await db.get_user(recipient.from_user.id)

    mailIDs = user2.data.get("mails", [])
    if not mail in user1.data.get("mails", []):
        await message.reply_text(f"**Mail didnt exist**")
        return
    limits = user2.get_limits()
    max_mails = limits["max_mails"]

    if len(mailIDs) >= max_mails:
        await message.reply_text(
            f"**Cannot transfer {mail} to {args[0]}.\nThis user had exhausted free mail limits.**"
        )
        return
    data = {"mails": mail.lower()}
    await user1.data.rm(data)
    await user2.data.addToSet(data)

    await client.send_message(
        args[0],
        f"""
**New mail transferred to your account.

`Mail `: {mail}
`Transferred by :` {message.reply_to_message.from_user.mention()}

Check your mails using /mails command.**""",
    )
    await message.reply_text(f"**Successfully transferred {mail} to {recipient.text}")
