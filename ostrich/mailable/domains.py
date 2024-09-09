from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.core import database as db
from bot.core import utils


@Client.on_message(filters.command(["adddomain"]))
async def adddomain(client, message):
    user = await db.get_user(message.from_user.id)

    if user.subscription["name"] != "premium":
        await message.reply(
            "You don't have a premium subscription.",
            reply_markup=(
                InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="Upgrade", callback_data="upgrade")]]
                )
            ),
        )
        return

    domain = await message.chat.ask("Send me your domain name")

    dataExists = await db.data_exists({"domains": domain.text})
    if dataExists:
        await client.send_message(message.chat.id, "Sorry this domain is unavailable")
        return
    mail_servers = utils.get_mx_server(domain.text)

    if "mx.bruva.co" in mail_servers:
        status = "▶"
        await message.reply("Domain verified")
        data = {"domains": domain.text}
        await user.data.addToSet(data)
        await db.inc_stat("domains", 1)
    else:
        status = "❌"
        text = f"""
Pending verification for {domain.text}

Add MX Record:
`mx.bruva.co`  {status}
"""
        await message.reply(
            text,
            reply_markup=(
                InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Check Status",
                                callback_data=f"chstatus_{domain.text}",
                            )
                        ]
                    ]
                )
            ),
        )


@Client.on_message(filters.command(["rmdomains", "rmdomain"]))
async def rmdomains(client, message):
    user = await db.get_user(message.from_user.id)

    if user.subscription["name"] == "premium":
        user_domains = user.data.get("domains", [])
        if len(user_domains) == 0:
            await message.reply_text("No domains found.")
        else:
            btn = ""
            for domain in user_domains:
                btn += f"[{domain}](data::dl_d:{domain})\n"

            keyboard = utils.generate_keyboard(btn)

            await message.reply_text(
                "Your domains:",
                disable_web_page_preview=True,
                reply_markup=keyboard,
                quote=True,
            )
