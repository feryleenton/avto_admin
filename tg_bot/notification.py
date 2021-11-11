import sys
# from .set_notif import cron
from telebot import TeleBot

bot = TeleBot('1606167426:AAEkbkfn4ciU7eu5A0ib9PpG0bMeuF1VnuU')


def send_notif(user_id):
    text = 'Текст оповещения'
    try:
        bot.send_message(user_id, text, parse_mode="HTML", reply_markup=None)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    arg = sys.argv
    user_id = arg[1]

    send_notif(user_id)

