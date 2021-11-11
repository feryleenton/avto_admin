import os

import flask
from flask import request, Flask
from telebot.types import Update

from tg_bot import bot
from time import sleep

os.environ['DJANGO_SETTINGS_MODULE'] = 'avto_admin.settings'

app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string)
        bot.process_new_updates([update])
        return '200'
    else:
        flask.abort(403)


if __name__ == '__main__':
    sleep(2)
    bot.remove_webhook()
    print(bot.get_me())
    bot.polling()

    # bot.set_webhook('https://185.233.118.83/bot', certificate=open('/home/admin/avto_bot/avto_admin/ssl_cert.crt', 'r'))
    # print(bot.get_webhook_info())
    #
    # app.run("0.0.0.0", port=5000, ssl_context=('/home/admin/avto_bot/avto_admin/ssl_cert.crt',
    #                                            '/home/admin/avto_bot/avto_admin/ssl_k.key'), debug=True)
