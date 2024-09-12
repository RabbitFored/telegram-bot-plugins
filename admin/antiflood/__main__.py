import time
from collections import defaultdict, deque
import os
from pyrogram import Client, filters
from bot.core import database as db

class AntiFlood:
    def __init__(self, max_messages, time_window):
        self.max_messages = max_messages
        self.time_window = time_window
        self.user_messages = defaultdict(deque)

    def is_flooding(self, user_id):
        current_time = time.time()
        message_times = self.user_messages[user_id]

        # Remove messages outside the time window
        while message_times and message_times[0] < current_time - self.time_window:
            message_times.popleft()

        # Check if user is flooding
        if len(message_times) >= self.max_messages:
            return True

        # Record the new message time
        message_times.append(current_time)
        return False
    def flush_user(self, user_id):
        """ Clears stored message times for a specific user. """
        if user_id in self.user_messages:
            del self.user_messages[user_id]


message_interval = os.environ.get("ANTIFLOOD_MESSAGE_INTERVAL", 5)
message_count = os.environ.get("ANTIFLOOD_MESSAGE_COUNT", 5)

antiflood = AntiFlood(message_count, message_interval)

@Client.on_message(filters.private , group=-10)
async def check_antiflood(client, message):
    userID = message.from_user.id
    if antiflood.is_flooding(userID):
        user = await db.get_user(userID)
        await user.warn()
        antiflood.flush_user(userID)
        await message.reply(
               "You are flooding me, slow down!\n\nFlooding may cause your account to be banned.")
        message.stop_propagation()
    else:
        message.continue_propagation()

        