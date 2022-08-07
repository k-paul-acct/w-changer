import logic

from vk_api.bot_longpoll import VkBotEventType

from config import GROUP_ID
from messages import *
from bot import Bot
from repository import Repository


def curr_week_msg() -> str:
    return ODD_WEEK if logic.get_curr_week_parity() else EVEN_WEEK

def start(bot: Bot):
    repository = Repository()
    for event in bot.longpoll.listen():
        chat_id = event.chat_id
        if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat:
            # Greeting message when the bot has been added to the conversation.
            if 'action' in event.message.keys() and event.message['action']['type'] == 'chat_invite_user':
                bot.send_message(chat_id, GREETING + curr_week_msg())

            # Message with setup instructions.
            elif ('@wchanger] помощь' in event.message.text or '@wchanger], помощь' in event.message.text):
                bot.send_message(chat_id, SETTING + curr_week_msg())

            # Setup process.
            elif '@wchanger]' in event.message.text:
                splitted = event.message.text.split('|')
                # If setup message is correct.
                if len(splitted) == 3:
                    even_week_name = splitted[1].replace('@wchanger]', '').strip(',').strip()
                    odd_week_name = splitted[2].strip()
                    # If the bot is an admin.
                    members = bot.get_chat_members(chat_id)
                    if members:
                        # If a user is an admin.
                        user_id = event.message.from_id
                        if bot.is_user_admin_in_chat(user_id, chat_id):
                            # Repository update.
                            repository.change_chat(chat_id, even_week_name, odd_week_name)
                            bot.send_message(chat_id, SUCCESS)
                            new_name = odd_week_name if logic.get_curr_week_parity() else even_week_name
                            bot.change_chat_title(chat_id, new_name)
                        else:
                            bot.send_message(chat_id, USER_IS_NOT_ADMIN)
                    else:
                        bot.send_message(chat_id, BOT_IS_NOT_ADMIN)
                else:
                    bot.send_message(chat_id, ERROR)
                    bot.send_message(chat_id, SETTING + curr_week_msg())
        print(chat_id, event.message)