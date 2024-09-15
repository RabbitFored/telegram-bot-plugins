import os
import tempfile

import aiofiles
import mailparser
from pyrogram.errors import InputUserDeactivated, UserIsBlocked
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from quart import Response, request

from bot import CONFIG, bot, logger, web
from bot.core import database as db

baseURL = CONFIG.baseURL


@web.route("/cust", methods=["POST"])
async def secretmessages():
    try:
        mailbytes = await request.get_data()
        mail = mailparser.parse_from_bytes(mailbytes)

        data = {
            "from": mail.from_,
            "to": mail.to,
            "cc": mail.cc,
            "bcc": mail.bcc,
            "subject": mail.subject,
            "body": mail.body,
            "text": mail.text_plain,
            "html": mail.text_html,
            "reply_to": mail.reply_to,
            "message_id": mail.message_id,
        }

        content = data["html"][0] if data["html"] else data["text"][0]

        # data = json.loads((await request.form).get("data"))

        user = await db.find_user({"mails": data["to"][0][1]})
        if not user:
            return "user not found"
        if user.status == "inactive":
            return "inactive user"
        text = f"\
  **Sender     :** {data['from'][0][1]}\n\
  **Recipient  :** {data['to'][0][1]}\n\
  **Subject    :** {data['subject']}\n\
  **Message    :** \n...\
  "

        with tempfile.TemporaryDirectory(prefix=f"{user.ID}_") as temp_dir:
            temp_file_path = os.path.join(temp_dir, "inbox.html")
            async with aiofiles.open(temp_file_path, "w") as temp_file:
                await temp_file.write(content)
                await temp_file.close()
            try:
                file = await bot.send_document(chat_id=user.ID, document=temp_file_path)
                await file.reply(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "View mail",
                                    web_app=WebAppInfo(
                                        url=f"{baseURL}/inbox/{user.ID}/{file.id}"
                                    ),
                                ),
                            ]
                        ]
                    ),
                    quote=True,
                )
            except UserIsBlocked:
                user.setStatus("inactive")
                return "blocked user"
            except InputUserDeactivated:
                await db.delete_user(user.ID)
                return "deactivated user"

        await db.inc_stat("recieved", 1)
        return Response(status=200)
    except Exception as e:
        logger.error(f"Something went wrong: {e}")
        return "something went wrong"
