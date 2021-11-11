import sys
import logging

from telebot import TeleBot, logger

logger.setLevel(logging.DEBUG)

sys.path.append('/home/admin/avto_bot/avto_admin/')
sys.path.append('/home/admin/avto_bot/avto_admin/avto_admin/')
sys.path.append('/home/admin/avto_bot/avto_admin/avto_admin/tg_bot/')


TOKEN = '1630483135:AAG5pA7f5PbnUnllYsoroMX3IuOluii1JQ8'  # prod
bot = TeleBot(TOKEN, parse_mode="HTML")


