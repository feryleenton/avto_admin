import datetime

from tg_bot.loader import bot
from tg_bot.keyboards import choice_time_key, add_comment_key, return_key, main_key, checkout, calendar_, del_cs_confirm_key, \
    payment_key

from main.models import Service as Serv
from main.models import Order as Order
from main.models import User as DbUser
from main.models import Cart as Cart
from main.models import CartService as CartService
from main.models import Notification
from ..user_data import *
from telebot.types import ReplyKeyboardRemove


@bot.callback_query_handler(func=lambda call: call.data.startswith("set_date_order:"))
def get_call(call):
    # try:
    print("\nCALL:", call.from_user)
    print("\nCALL DATA:", call.data)
    user_id = call.from_user.id
    user = get_user_data(user_id)

    db_user = DbUser.objects.get(user_id=user_id)

    bot.delete_message(user_id, call.message.message_id)

    # cart_id = call.data.split(":")[-1]

    cart = Cart.objects.filter(user=db_user, in_order=False).first()
    user.cart_id = cart.id

    print("\nCART:", cart)

    if not user.order_comment:
        user.order_comment = " "
        ####################################################################################################
    new_order = Order.objects.get(related_cart=cart)

    try:
        cart = Cart.objects.get(user=db_user, order=new_order, in_order=False)
    except Exception as e:
        print(e)

    cart_items = cart.services.all()
    print(cart_items)
    services = ''
    total_price = 0
    for n, cart_service in enumerate(cart_items, start=1):
        title = str(cart_service).split(" ", maxsplit=1)[-1]

        print(cart_service)

        total_price += cart_service.service.price

        services += str(n) + ". " + title + " - " + str(cart_service.service.price) + " ₴\n"
    if cart.total_price != total_price:
        cart.total_price = total_price

    cart.save()

    bot.send_message(user_id, f"<b>Корзина:</b>\n\n<i> {services} </i>\n"
                          f"<b>Общая стоимость:</b> <i>{cart.total_price} {cart.currency.upper()}</i>",
                              f"Выберите дату:",
                     reply_markup=calendar_(cart.id), parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data.startswith("add_to_cart:"))
def get_call(call):
    # try:
    print("\nCALL:", call.from_user)
    print("\nCALL DATA:", call.data)
    user_id = call.from_user.id

    user = get_user_data(user_id)

    # bot.delete_message(user_id, call.message.message_id)

    serv_id = call.data.split(":")[-1]
    service = Serv.objects.get(id=serv_id)
    user.service_id = serv_id
    print("\nSERV:", service)
    db_user = DbUser.objects.get(user_id=user_id)

    user.auto_type = 'sedan'
    if not user.order_comment:
        user.order_comment = " "
        ####################################################################################################

    new_order, exists = Order.objects.get_or_create(user=db_user, confirmed=False)
    print("new_order exists ", new_order, new_order.id)
    user.order_id = new_order.id

    cart, exists = Cart.objects.get_or_create(user=db_user, order=new_order, in_order=False)
    print("cart exists:", exists)

    cart_service = CartService.objects.create(user=db_user, service=service, cart=cart)
    print("service.currency", service.currency)
    cart_service.total_price = service.price
    cart_service.currency = service.currency
    cart_service.save()

    cart.services.add(cart_service)
    cart.currency = service.currency
    cart.save()
    cart_items = cart.services.all()

    print(cart_items)
    services = ''
    total_price = 0
    for n, cart_service in enumerate(cart_items, start=1):
        title = str(cart_service).split(" ", maxsplit=1)[-1]

        print(cart_service)

        total_price += cart_service.service.price

        services += str(n) + ". " + title + " - " + str(cart_service.service.price) + " ₴\n"
    if cart.total_price != total_price:
        cart.total_price = total_price

    cart.save()

    bot.edit_message_text(f"<b>Корзина:</b>\n\n<i> {services} </i>\n"
                          f"<b>Общая стоимость:</b> <i>{cart.total_price} {cart.currency.upper()}</i>",
                          user_id,
                          call.message.message_id,
                          reply_markup=checkout(cart.id))


@bot.callback_query_handler(func=lambda call: call.data.startswith("order:"))
def get_call(call):
    # try:
    print("\nCALL:", call.from_user)
    print("\nCALL DATA:", call.data)
    user_id = call.from_user.id
    db_user = DbUser.objects.get(user_id=user_id)

    user = get_user_data(user_id)

    # bot.delete_message(user_id, call.message.message_id)

    date = call.data.split("_")[-1].split(":")[-1]

    cart_id = call.data.split("_")[0].split(":")[-1]

    cart, created = Cart.objects.get_or_create(user=db_user, in_order=False)

    print("created", created, "in order:", cart.in_order)
    print(date)
    user_date = datetime.datetime.strptime(date, '%d %m %Y').date()
    check_date = datetime.datetime.strptime(date, "%d %m %Y").date()
    user.order_date = check_date

    user.cart_id = cart_id
    print("\nCART:", cart)
    ####################################################################################################

    new_order = Order.objects.get(user=db_user, related_cart=cart)
    new_order.lead_time = check_date
    new_order.save()
    # cart = Cart.objects.get(user=db_user, order=new_order, in_order=False)

    cart_items = cart.services.all()
    print(cart_items)
    services = ''
    total_price = 0
    for n, cart_service in enumerate(cart_items, start=1):
        title = str(cart_service).split(" ", maxsplit=1)[-1]

        print(cart_service)

        total_price += cart_service.service.price

        services += str(n) + ". " + title + " - " + str(cart_service.service.price) + " ₴\n"
    if cart.total_price != total_price:
        cart.total_price = total_price

    cart.save()

    # bot.send_message(user_id, f"<b>Корзина:</b>\n\n<i> {services} </i>\n"
    #                           f"<b>Общая стоимость:</b> <i>{cart.total_price} </i>\n\n"
    #                           f"<b>Дата:</b> {user_date}\n"
    #                           f"Укажите время",
    #                  reply_markup=choice_time_key(cart.id, date), parse_mode="HTML")
    bot.edit_message_text(f"<b>Корзина:</b>\n\n<i> {services} </i>\n"
                          f"<b>Общая стоимость:</b> <i>{cart.total_price} </i>\n\n"
                          f"<b>Дата:</b> {user_date}\n"
                          f"\n<b>Укажите время:</b>",
                          user_id, call.message.message_id, reply_markup=choice_time_key(cart.id, date))
    # except Exception as e:
    #     print("\nGET_CALL 'order:':", e)


@bot.callback_query_handler(func=lambda call: call.data.startswith("order_time-"))
def get_call(call):
    try:
        print("\nCALL:", call.from_user)
        print("\nCALL DATA:", call.data)
        user_id = call.from_user.id
        user = get_user_data(user_id)

        bot.delete_message(user_id, call.message.message_id)
        cart = Cart.objects.get(user__user_id=user_id, in_order=False)

        new_order = Order.objects.get(related_cart=cart)

        order_time = call.data.split("-")[-1]
        order_time = datetime.datetime.strptime(order_time, "%H:%M").time()
        new_order.time_slot = order_time
        new_order.save()

        cart_items = cart.services.all()
        print(cart_items)
        services = ''
        total_price = 0
        for n, cart_service in enumerate(cart_items, start=1):
            title = str(cart_service).split(" ", maxsplit=1)[-1]

            print(cart_service)

            total_price += cart_service.service.price

            services += str(n) + ". " + title + " - " + str(cart_service.service.price) + " ₴\n"
        if cart.total_price != total_price:
            cart.total_price = total_price

        cart.save()

        user.order_time = order_time

        bot.send_message(user_id, f"<b>Корзина:</b>\n\n<i> {services} </i>\n"
                          f"<b>Общая стоимость:</b> <i>{cart.total_price} {cart.currency.upper()}</i>",
                                  f"<b>Выбранная дата:</b> <i>{user.order_date}\n\n</i>"
                                  f"<b>Выбранное время:</b> <i>{user.order_time}</i>",
                         reply_markup=add_comment_key(user.service_id, user.order_date), parse_mode="HTML")
    except Exception as e:
        print("\nGET_CALL 'order_time:", e)


@bot.callback_query_handler(func=lambda call: call.data.startswith("add_comment"))
def get_call_comment(call):
    print("\nCALL:", call.from_user)
    print("\nCALL DATA:", call.data)
    try:
        user_id = call.from_user.id
        user = get_user_data(user_id)

        bot.delete_message(user_id, call.message.message_id)

        cart = Cart.objects.get(id=user.cart_id)

        cart_items = cart.services.all()
        print(cart_items)
        services = ''
        total_price = 0
        for n, cart_service in enumerate(cart_items, start=1):
            title = str(cart_service).split(" ", maxsplit=1)[-1]

            print(cart_service)

            total_price += cart_service.service.price

            services += str(n) + ". " + title + " - " + str(cart_service.service.price) + " ₴\n"
        if cart.total_price != total_price:
            cart.total_price = total_price

        cart.save()

        m = bot.send_message(user_id, f"<b>Корзина:</b>\n\n<i> {services} </i>\n"
                          f"<b>Общая стоимость:</b> <i>{cart.total_price} {cart.currency.upper()}</i>",
                                      f"<b>Выбранная дата:</b> <i>{user.order_date}\n\n</i>"
                                      f"<b>Выбранное время:</b> <i>{user.order_time}</i>\n\n"
                                      f"<b>Введите комментарий к заказу:</b>",
                             reply_markup=return_key(), parse_mode="HTML")
        bot.register_next_step_handler(m, get_comment)
    except Exception as e:
        print("\nGET_CALL_COMMENT EX:", e)


def get_comment(message):
    print("\n", message.from_user)
    print("\nComment:", message.text)
    user_id = message.from_user.id

    user = get_user_data(user_id)

    bot.delete_message(user_id, message.message_id - 1)
    bot.delete_message(user_id, message.message_id)

    new_order = Order.objects.filter(user__user_id=user_id).first()
    cart = Cart.objects.get(id=user.cart_id)

    cart_items = cart.services.all()
    print(cart_items)
    services = ''
    total_price = 0
    for n, cart_service in enumerate(cart_items, start=1):
        title = str(cart_service).split(" ", maxsplit=1)[-1]

        print(cart_service)

        total_price += cart_service.service.price

        services += str(n) + ". " + title + " - " + str(cart_service.service.price) + " ₴\n"
    if cart.total_price != total_price:
        cart.total_price = total_price

    if message.text.__contains__("Вернуться"):
        bot.send_message(user_id, f"<b>Корзина:</b>\n\n<i> {services} </i>\n"
                          f"<b>Общая стоимость:</b> <i>{cart.total_price} {cart.currency.upper()}</i>",
                                  f"<b>Выбранная дата:</b> <i>{user.order_date}\n\n</i>"
                                  f"<b>Выбранное время:</b> <i>{user.order_time}</i>",
                         reply_markup=add_comment_key(user.cart_id, user.order_date), parse_mode="HTML")
    else:
        msg = bot.send_message(user_id, f"Комментарий - {message.text}\n\nУспешно добавлен!",
                               reply_markup=ReplyKeyboardRemove())
        bot.delete_message(user_id, msg.message_id, timeout=2)
        new_order.comment = message.text
        new_order.save()
        bot.send_message(user_id,
                         f"<b>Корзина:</b>\n\n<i> {services} </i>\n"
                          f"<b>Общая стоимость:</b> <i>{cart.total_price} {cart.currency.upper()}</i>",
                         f"<b>Выбранная дата:</b> <i>{user.order_date}\n\n</i>"
                         f"<b>Выбранное время:</b> <i>{user.order_time}</i>\n\n"
                         f"<b>Комментарий:</b> <i>{new_order.comment}</i>",
                         reply_markup=add_comment_key(user.cart_id, user.order_date), parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_cash:"))
def get_call_confirm_order(call):
    user_id = call.from_user.id

    new_order = Order.objects.get(id=int(call.data.split(":")[-1]))
    user = get_user_data(user_id)
    cart = Cart.objects.filter(order=new_order)

    bot.send_message(user_id, 'Спасибо, мы вскоре вам позвоним, чтобы уточнить бронь.', reply_markup=main_key())
    managers = Notification.objects.all()

    cart_items = cart.services.all()
    print(cart_items)
    services = ''
    total_price = 0
    for n, cart_service in enumerate(cart_items, start=1):
        title = str(cart_service).split(" ", maxsplit=1)[-1]

        print(cart_service)

        total_price += cart_service.service.price

        services += str(n) + ". " + title + " - " + str(cart_service.service.price) + " ₴\n"
    if cart.total_price != total_price:
        cart.total_price = total_price

    for manager in managers:
        try:
            # bot.send_message(manager.username, "")

            bot.send_message(manager.user_id, f"<b>Список услуг:</b>\n\n<i> {services} </i>\n"
                                              f"<b>Общая стоимость:</b> <i>{cart.total_price} {cart.currency.upper()}</i>",
                             f"<b>Выбранная дата:</b> <i>{user.order_date}\n\n</i>"
                             f"<b>Выбранное время:</b> <i>{user.order_time}</i>\n\n"
                             f"Вы можете оплатить заказ картой или с помощью Apple Pay")
        except Exception as e:
            print("send to manager error:", e)


@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_order"))
def get_call_confirm_order(call):
    user_id = call.from_user.id

    print("\nCALL:", call.from_user)
    print("\nCALL DATA:", call.data)
    user = get_user_data(user_id)
    try:

        bot.delete_message(user_id, call.message.message_id)

        db_user = DbUser.objects.get(user_id=user_id)
        cart = Cart.objects.get(user=db_user, in_order=False)

        cart.in_order = True

        cart.save()
        ####################################################################################################
        new_order = Order.objects.get(related_cart=cart)
        new_order.confirmed = True
        print("\nNEW_ORDER", new_order)
        new_order.save()
        ##################################################################################################

        ###
        # set_notif(user_id, user.order_date, user.order_time, order=f"{new_order.id} {new_order.user}")
        ###

        # bot.send_message(user_id, 'Спасибо, мы вскоре вам позвоним, чтобы уточнить бронь.', reply_markup=main_key())
        bot.send_message(user_id, 'Вы можете оплатить заказ картой или с помощью Apple Pay', reply_markup=payment_key(new_order))

        managers = Notification.objects.all()

        cart_items = cart.services.all()
        print(cart_items)
        services = ''
        total_price = 0
        for n, cart_service in enumerate(cart_items, start=1):
            title = str(cart_service).split(" ", maxsplit=1)[-1]

            print(cart_service)

            total_price += cart_service.service.price

            services += str(n) + ". " + title + " - " + str(cart_service.service.price) + " ₴\n"
        if cart.total_price != total_price:
            cart.total_price = total_price

        for manager in managers:
            try:
                # bot.send_message(manager.username, "")

                bot.send_message(manager.user_id, f"<b>Список услуг:</b>\n\n<i> {services} </i>\n"
                                                  f"<b>Общая стоимость:</b> <i>{cart.total_price} {cart.currency.upper()}</i>",
                                 f"<b>Выбранная дата:</b> <i>{user.order_date}\n\n</i>"
                                 f"<b>Выбранное время:</b> <i>{user.order_time}</i>\n\n"
                                 f"Вы можете оплатить заказ картой или с помощью Apple Pay")
            except Exception as e:
                print("send to manager error:", e)

    except Exception as e:
        print("\nGET_CALL_CONFIRM_ORDER:", e)


# express

@bot.callback_query_handler(func=lambda call: call.data == "express")
def get_call_confirm_order(call):
    user_id = call.from_user.id

    print("\nCALL:", call.from_user)
    print("\nCALL DATA:", call.data)

    user = get_user_data(user_id)

    # bot.delete_message(user_id, call.message.message_id)

    service = Serv.objects.get(title='Фулл-Контакт')
    user.service_id = service.id
    print("\nSERV:", service)
    db_user = DbUser.objects.get(user_id=user_id)

    new_order, exists = Order.objects.get_or_create(user=db_user, confirmed=False)
    print("new_order", new_order, new_order.id)
    user.order_id = new_order.id

    cart, exists = Cart.objects.get_or_create(user=db_user, order=new_order, in_order=False)
    print("exists:", exists)

    cart_service = CartService.objects.create(user=db_user, service=service, cart=cart)
    cart_service.total_price = service.price
    cart_service.currency = service.currency
    cart_service.save()

    cart.services.add(cart_service)
    cart.currency = service.currency
    cart.save()
    cart_items = cart.services.all()

    print(cart_items)
    services = ''
    total_price = 0
    for n, cart_service in enumerate(cart_items, start=1):
        title = str(cart_service).split(" ", maxsplit=1)[-1]

        print(cart_service)

        total_price += cart_service.service.price

        services += str(n) + ". " + title + " - " + str(cart_service.service.price) + " ₴\n"
    if cart.total_price != total_price:
        cart.total_price = total_price

    cart.save()

    bot.edit_message_text(f"<b>Корзина:</b>\n\n<i> {services} </i>\n"
                          f"<b>Общая стоимость:</b> <i>{cart.total_price} {cart.currency.upper()}</i>",
                          user_id,
                          call.message.message_id,
                          reply_markup=checkout(cart.id))


@bot.callback_query_handler(func=lambda call: call.data.startswith("del_cs:"))
def get_call_delete(call):
    try:

        print("\nCALL:", call.from_user)
        user_id = call.from_user.id
        db_user = DbUser.objects.get(user_id=user_id)
        cs_id = call.data.split(":")[-1]

        cart_service = Cart.objects.filter(user=db_user, in_order=False).first().services.get(id=cs_id)
        title = str(cart_service).split(" ", maxsplit=1)[-1]
        bot.edit_message_text(f"Вы действительно хотите удалить  {title} из корзины?",
                              user_id, call.message.message_id, reply_markup=del_cs_confirm_key(cs_id)
                              )

    except Exception as e:
        print("\nGET_CALL delete:", e)


@bot.callback_query_handler(func=lambda call: call.data == "n_cs_del")
def get_call_confirm_order(call):
    user_id = call.from_user.id

    print("\nCALL:", call.from_user)
    print("\nCALL DATA:", call.data)

    user = get_user_data(user_id)

    # bot.delete_message(user_id, call.message.message_id)

    db_user = DbUser.objects.get(user_id=user_id)
    if not user.order_comment:
        user.order_comment = " "
        ####################################################################################################

    new_order, exists = Order.objects.get_or_create(user=db_user, confirmed=False)
    print("new_order", new_order, new_order.id)
    user.order_id = new_order.id

    cart, exists = Cart.objects.get_or_create(user=db_user, order=new_order, in_order=False)
    if not exists:
        print("exists:", exists)

        # cart_service = CartService.objects.create(user=db_user, service=service, cart=cart)
        # cart_service.total_price = service.price
        # cart_service.save()
        #
        # cart.services.add(cart_service)
        # cart.save()
        cart_items = cart.services.all()

        print(cart_items)
        services = ''
        total_price = 0
        for n, cart_service in enumerate(cart_items, start=1):
            title = str(cart_service).split(" ", maxsplit=1)[-1]

            print(cart_service)

            total_price += cart_service.service.price

            services += str(n) + ". " + title + " - " + str(cart_service.service.price) + " ₴\n"

        if cart.total_price != total_price:
            cart.total_price = total_price

        cart.save()

        bot.edit_message_text(f"<b>Корзина:</b>\n\n<i> {services} </i>\n"
                              f"<b>Общая стоимость:</b> <i>{cart.total_price} {cart.currency.upper()}</i>",
                              user_id,
                              call.message.message_id,
                              reply_markup=checkout(cart.id))


@bot.callback_query_handler(func=lambda call: call.data.startswith("y_cs_del:"))
def get_call_confirm_order(call):
    user_id = call.from_user.id

    print("\nCALL:", call.from_user)
    print("\nCALL DATA:", call.data)

    user = get_user_data(user_id)
    db_user = DbUser.objects.get(user_id=user_id)
    cs_id = call.data.split(":")[-1]

    # bot.delete_message(user_id, call.message.message_id)

    ####################################################################################################

    new_order, exists = Order.objects.get_or_create(user=db_user, confirmed=False)
    print("new_order", new_order, new_order.id)
    user.order_id = new_order.id

    cart, exists = Cart.objects.get_or_create(user=db_user, order=new_order, in_order=False)
    if not exists:
        print("cart exists:", exists)
        cs = cart.services.get(id=int(cs_id))
        cs.delete()
        cart_items = cart.services.all()

        print(cart_items)
        services = ''
        total_price = 0
        for n, cart_service in enumerate(cart_items, start=1):
            title = str(cart_service).split(" ", maxsplit=1)[-1]

            print(cart_service)

            total_price += cart_service.service.price

            services += str(n) + ". " + title + " - " + str(cart_service.service.price) + " ₴\n"

        if cart.total_price != total_price:
            cart.total_price = total_price

        cart.save()

        bot.edit_message_text(f"<b>Корзина:</b>\n\n<i> {services} </i>\n"
                              f"<b>Общая стоимость:</b> <i>{cart.total_price} {cart.currency.upper()}</i>",
                              user_id,
                              call.message.message_id,
                              reply_markup=checkout(cart.id))


##########################################################

from telebot.types import LabeledPrice, ShippingOption

provider_token = '632593626:TEST:sandbox_i83896887146'  # @BotFather -> Bot Settings -> Payments

shipping_options = [
    ShippingOption(id='instant', title='WorldWide Teleporter').add_price(LabeledPrice('Teleporter', 1000)),
    ShippingOption(id='pickup', title='Local pickup').add_price(LabeledPrice('Pickup', 300))]


@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_order:"))
def command_pay(call):
    user_id = call.from_user.id

    user = get_user_data(user_id)

    # bot.delete_message(user_id, call.message.message_id)

    order_id = call.data.split(":")[-1]
    user.order_id = order_id
    print("\nOrder_id:", order_id)
    db_user = DbUser.objects.get(user_id=user_id)

    new_order = Order.objects.get(user=db_user, id=int(order_id))
    print("new_order exists ", new_order, new_order.id)
    user.order_id = new_order.id

    cart = Cart.objects.filter(user=db_user, order=new_order).first()
    cart_items = cart.services.all()

    print(cart_items)
    services = ''
    total_price = 0
    for n, cart_service in enumerate(cart_items, start=1):
        title = str(cart_service).split(" ", maxsplit=1)[-1]

        print(cart_service)

        total_price += cart_service.service.price

        services += str(n) + ". " + title + " - " + str(cart_service.service.price) + " ₴\n"
    if cart.total_price != total_price:
        cart.total_price = total_price

    cart.save()
    prices = [LabeledPrice(label=f'{str(new_order)}', amount=int(round(float(cart.total_price))) * 100)]

    bot.send_invoice(user_id,
                     title=str(new_order),
                     description=f"Оплата заказа: {new_order.id}; Общая стоимость {cart.total_price} {cart.currency.upper()}",
                     provider_token=provider_token,
                     currency=str(cart.currency),
                     photo_url=None,
                     photo_height=None,  # !=0/None or picture won't be shown
                     photo_width=None,
                     photo_size=None,
                     is_flexible=False,  # True If you need to set up Shipping Fee
                     prices=prices,
                     start_parameter='example',
                     invoice_payload=f'Заказ № {new_order.id}')


@bot.shipping_query_handler(func=lambda query: True)
def shipping(shipping_query):
    print(shipping_query)
    bot.answer_shipping_query(shipping_query.id, ok=True, shipping_options=shipping_options,
                              error_message='Oh, seems like our Dog couriers are having a lunch right now. Try again later!')


@bot.pre_checkout_query_handler(func=lambda query: True)
def pay_checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Вы указали не верные реквизиты оплаты, или вас недостаточно средств,"
                                                "повторите попытку позже!")


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    print(message)
    print(message.successful_payment.invoice_payload)
    order_id = message.successful_payment.invoice_payload.split(" ")[-1]
    print(order_id)
    order = Order.objects.get(id=int(order_id))
    order.status = '2'
    order.save()
    bot.send_message(message.chat.id,
                     'Оплата прошла успешно!\nЗаказ № `{} \nСтоимость:{}` '.format(
                         message.successful_payment.total_amount / 100, message.successful_payment.currency),

                     parse_mode='Markdown', reply_markup=main_key())
