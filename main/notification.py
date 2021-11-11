import sys
from telebot import TeleBot
TOKEN = '1404149920:AAGHnL8jX4zAuldB4B_gYt2KojZfERlBJR8'

# bot = TeleBot('1606167426:AAEkbkfn4ciU7eu5A0ib9PpG0bMeuF1VnuU')
bot = TeleBot(TOKEN)


def send_notif(user_id):
    text = 'Текст оповещения'
    bot.send_message(user_id, text, parse_mode="HTML", reply_markup=None)


if __name__ == '__main__':
    arg = sys.argv
    user_id = arg[1]

    send_notif(user_id)
