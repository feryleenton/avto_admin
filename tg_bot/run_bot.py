# coding=utf-8
import os
import sys

import django

from tg_bot import bot
from telebot import types

from user_data import (get_user_data, auto_types)
from keyboards import main_key, phone_request_key, query_service_key, serv_key, query_select_auto_type_key

django.setup()

from main.models import User as DbUser, Order, Notification
from main.models import Category as Category
from main.models import Service as Serv
from main.models import Auto


@bot.message_handler(commands=['start'])
def first(message):
    print("\n", message.from_user, "\n", message.text)
    user_id = message.from_user.id
    user = get_user_data(user_id)
    bot.clear_step_handler_by_chat_id(user_id)

    if message.from_user.username:
        user.username = message.from_user.username
    else:
        user.username = " "

    if message.from_user.last_name:
        user.last_name = message.from_user.last_name
    else:
        user.last_name = " "

    db_user, exists = DbUser.objects.get_or_create(user_id=user_id)

    db_user.first_name = message.from_user.first_name
    db_user.last_name = user.last_name
    db_user.username = user.username
    db_user.user_id = user_id
    db_user.save()

    new_order = Order.objects.filter(user=db_user, confirmed=False).delete()
    if not db_user.phone_number:
        bot.send_message(user_id, "Для работы с ботом отправьте ваш номер телефона.",
                         reply_markup=phone_request_key())
    else:
        bot.send_message(db_user.user_id, 'Главное меню:', reply_markup=main_key())


@bot.message_handler(content_types=['contact'])
def get_phone(message):
    user_id = message.from_user.id
    bot.delete_message(user_id, message.message_id)
    user = get_user_data(user_id)

    user.phone_number = str(message.contact.phone_number).replace("+", "")

    new_user = DbUser.objects.get(user_id=user_id)

    new_user.phone_number = user.phone_number
    new_user.save()

    try:
        manager = Notification.objects.filter(phone_number=user.phone_number).first()
        manager.user_id = user_id
        if message.from_user.username:
            manager.username = message.from_user.username
        manager.save()
    except Exception as e:
        print(e)

    m = bot.send_message(user_id, "Укажите марку и модель вашего вашего автомобиля:"
                                  "\nНапример: <i>Volkswagen Golf</i>")
    bot.register_next_step_handler(m, set_auto_brand)


def set_auto_brand(message):
    user_id = message.from_user.id
    print(message.text)

    db_user = DbUser.objects.get(user_id=user_id)
    new_auto = Auto.objects.create(owner=db_user)

    new_auto.brand = message.text
    new_auto.save()

    m = bot.send_message(user_id, "Укажите тип кузова вашего автомобиля:", reply_markup=query_select_auto_type_key())
    bot.register_next_step_handler(m, set_auto_type)


def set_auto_type(message):
    user_id = message.from_user.id
    print(message.text)
    auto_type = message.text.split("Тип кузова: ")[-1].strip()
    print("auto_type", auto_type)

    db_user = DbUser.objects.get(user_id=user_id)
    new_auto = Auto.objects.get(owner=db_user)

    for key, value in auto_types.items():
        if value == auto_type:
            new_auto.auto_class = key
            new_auto.save()

    # m = bot.send_message(user_id, "Укажите модель автомобиля")
    # bot.register_next_step_handler(m, set_auto_model)

    m = bot.send_message(user_id, "Укажите номер автомобиля")
    bot.register_next_step_handler(m, set_auto_number)


def set_auto_number(message):
    user_id = message.from_user.id
    print(message.text)

    db_user = DbUser.objects.get(user_id=user_id)
    new_auto = Auto.objects.get(owner=db_user)
    new_auto.number = message.text
    new_auto.save()

    bot.send_message(user_id, "Главное меню", reply_markup=main_key())


@bot.message_handler(content_types=['text'])
def first(message):
    print("\n", message.from_user, "\n", message.text)
    user_id = message.from_user.id

    if message.text == 'Кабинет':

        try:
            db_user = DbUser.objects.get(user_id=user_id)
            bot.send_message(user_id, f'Кабинет пользователя: {str(db_user)}')
        except Exception as e:
            db_user = None
            m = bot.send_message(user_id, "Для работы с ботом отправьте ваш номер телефона",
                                 reply_markup=phone_request_key())
            bot.register_next_step_handler(m, get_phone)

        user = get_user_data(user_id)

    elif message.text.__contains__("Услуга: "):
        try:
            serv_title = message.text.split("Услуга: ")[-1].rstrip().strip()

            service = Serv.objects.get(title=serv_title)
            print(service)
            bot.delete_message(user_id, message.id)

            bot.send_message(user_id,
                             f"<b>Услуга:</b> <i><code>{service.title}</code></i>\n\nОписание:\n"
                             f"<code>{service.description}</code>\n\nЦена: {service.price} UAH",
                             reply_markup=serv_key(service))

        except Exception as e:
            print(e)


@bot.inline_handler(func=lambda query: query.query.startswith('Категории'))
def query_text(query):
    print(query)
    categories = Category.objects.filter(show=True)
    print(categories)
    answer = []
    for n, cat in enumerate(categories):
        text = types.InlineQueryResultArticle(
            id=n,
            title=cat.title,
            description=cat.title,
            reply_markup=query_service_key(cat),
            thumb_url="https://pp.vk.me/c627626/v627626512/2a627/7dlh4RRhd24.jpg",

            input_message_content=types.InputTextMessageContent(
                message_text=f"Категория: {cat.title}",
                parse_mode="HTML")

        )

        answer.append(text)

    bot.answer_inline_query(query.id, answer)


@bot.inline_handler(func=lambda query: query.query.startswith('Категория'))
def query_text(query):
    print(query)
    print(query.query)
    try:
        title = query.query.split(":")[-1].rstrip().strip()

        print(title)
        category = Category.objects.get(title=title)
        print("\nCATEGORY", category)

        services = Serv.objects.filter(category=category)
        print(services)
        answer = []
        for n, service in enumerate(services):
            text = types.InlineQueryResultArticle(
                id=n,
                title=service.title,
                description=str(service.price), reply_markup=None,
                thumb_url="https://pp.vk.me/c627626/v627626512/2a627/7dlh4RRhd24.jpg",

                input_message_content=types.InputTextMessageContent(
                    message_text=f"Категория: <b>{category.title}</b>\nУслуга: <b>{service.title}</b>",
                    parse_mode="HTML",
                    disable_web_page_preview=True))

            answer.append(text)

        bot.answer_inline_query(query.id, answer)
    except Exception as e:
        print(e)


@bot.inline_handler(func=lambda query: query.query.startswith('Тип кузова'))
def query_text(query):
    print(query)
    print(query.query)

    types_of_auto = auto_types.values()
    try:

        answer = []
        for n, auto_type in enumerate(types_of_auto):
            text = types.InlineQueryResultArticle(
                id=n,
                title=auto_type, reply_markup=None,
                thumb_url="https://pp.vk.me/c627626/v627626512/2a627/7dlh4RRhd24.jpg",

                input_message_content=types.InputTextMessageContent(
                    message_text=f"Тип кузова: <b>{auto_type}</b>",
                    parse_mode="HTML",
                    disable_web_page_preview=True))

            answer.append(text)

        bot.answer_inline_query(query.id, answer)
    except Exception as e:
        print(e)


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
