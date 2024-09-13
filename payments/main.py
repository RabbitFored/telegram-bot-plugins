'''
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButtonBuy, InlineKeyboardMarkup, LabeledPrice
from bot.core.utils import generate_keyboard
from pyrogram.enums import ListenerTypes, MessageEntityType
from bot import CONFIG
@Client.on_message(filters.command(["pay"]))
async def new_payment(client, message):
      btn = '
[Telegram Stars](data::pay_stars)
[Crypto](data::pay_crypto)'
      op = await message.reply("Choose a payment method:",reply_markup=generate_keyboard(btn))
      l = await client.listen(
      message_id=op.id, listener_type=ListenerTypes.CALLBACK_QUERY
  )
      await l.answer()
      await op.delete()
      if l.data == "pay_stars":
        await client.send_invoice(
            message.chat.id,
            title="Subscribe | Monthly",
            description="Subscribe to mailable premium for a month",
            currency="XTR",
            prices=[LabeledPrice(label="Mailable Premium", amount=50)],
            start_parameter="start",
            reply_markup=(
                InlineKeyboardMarkup([[InlineKeyboardButtonBuy(text="Pay ⭐️50")]])
            ),
        )
      elif l.data == "pay_crypto":
        await l.message.reply("pay_crypto")
      else:
        await l.message.reply("unknown payment method")


@Client.on_message(filters.command(["pay1"]))
async def new_payment1(client, message):
  subscriptions = CONFIG.settings["subscriptions"]
  pars = {}
  for sub in subscriptions:
    name = sub["name"]
    if name == "free":
      continue
    pars[sub["name"]] = {}
    for p in sub["data"]["prices"]:
      title = p["title"].lower()
      pars[sub["name"]][title] = {}
      pars[sub["name"]][title]["price"] = p["price"]
      pars[sub["name"]][title]["validity"] = p["validity"]
      
  print(pars)
  
  b1 = ""
  for s in pars:
    b1 += f"[{s}](data::pay_{s})\n"
  a1 = await message.reply("Select a plan:",reply_markup=generate_keyboard(b1))
  r1 = await client.listen(message_id=a1.id, listener_type=ListenerTypes.CALLBACK_QUERY)

  await r1.answer()
  await a1.delete()

  b2 = ""
  data1 = r1.data.split("_")[-1]
  for p in pars[data1]:
        b2 += f"[{p}](data::pay_{data1}_{p.lower()})\n"
  a2 = await message.reply("Choose a :",reply_markup=generate_keyboard(b2))
  r2 = await client.listen(message_id=a2.id, listener_type=ListenerTypes.CALLBACK_QUERY)

  '''