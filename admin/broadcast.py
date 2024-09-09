#from mailable import logger, CONFIG, PROCESSES
import asyncio

from pyrogram import Client, filters
from pyrogram.errors import (
    FloodWait,
    InputUserDeactivated,
    PeerIdInvalid,
    UserIsBlocked,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot import CONFIG, ProcessManager, logger
from bot.core import database as db
from bot.core import filters as fltr


async def bcast(mode, msg, process):
    process.data["x"] = 0
    process.data["failed"] = 0
    
    users = await db.fetch_all_users()
    process.data["total"] = len(users)
    for user in users:
        try:
            if mode == "copy":
                await msg.copy(user)
            else:
                await msg.forward(user)
            process.data["x"] += 1
        except FloodWait as e:
            process.data["failed"]+= 1
            await asyncio.sleep(e.value)
            logger.info("FloodWait: " + str(e))
        except UserIsBlocked:
            process.data["failed"]+= 1
            dser = await db.get_user(user)
            await dser.setStatus("inactive")
        except InputUserDeactivated:
            process.data["failed"]+= 1 
            await db.delete_user(user)
            logger.info(f"removed deactivated user {user} from db")
        except PeerIdInvalid:
            process.data["failed"]+= 1 
            logger.info(f"{user} : peer id invalid\n")
            # db.delete_user(user)
        except Exception as e:
            process.data["failed"]+= 1 
            logger.info(f"Error: {e}")
        
@Client.on_message(filters.command(["broadcast"]) & fltr.group("admin"))
async def broadcast(client, message):
        processes = ProcessManager.list_processes()
       
        for p in processes:

            if p.name == 'broadcast':
                await message.reply_text("Another broadcast is already in progress. Please try again later.")
                return
        
        broadcast_msg = message.reply_to_message
    
        if not broadcast_msg:
            await message.reply(
                "Please reply to a message to broadcast it.", quote=True
            )
            return


        mode = CONFIG.settings["broadcast"]["mode"]
        if len(message.text.split(" ")) > 1:
            mode = message.text.split(" ")[1]
            
        process = ProcessManager.create_process("broadcast")
        print(process.process_id)
        keyboard = [
        [
            InlineKeyboardButton("Check Progress", callback_data=f"ps_{process.process_id}"),
        ]
    ]
        await message.reply_text("Broadcasting...",                                                    reply_markup=InlineKeyboardMarkup(keyboard))

        await process.start( bcast( mode, broadcast_msg, process ) )  
    
