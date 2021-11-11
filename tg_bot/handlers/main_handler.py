from tg_bot.loader import bot

from tg_bot.keyboards import main_key, category_key, check_orders_key, del_order_confirm_key

from main.models import Order as Order
from main.models import User as DbUser
from main.models import Cart as Cart

STATUS = {
    "0": "Заявка",
    "1": "Забронирован",
    '2': 'Оплачен',
    "3": "Выполняется",
    "4": "Выполнен"
}


@bot.callback_query_handler(func=lambda call: call.data == "main")
def get_main(call):
    try:
        print("\nCALL:", call.from_user)
        user_id = call.from_user.id
        bot.delete_message(user_id, call.message.message_id)
        bot.send_message(user_id, "Главное меню", reply_markup=main_key())
    except Exception as e:
        print("\nGET_CALL:", e)


@bot.callback_query_handler(func=lambda call: call.data == "about")
def get_call(call):
    try:
        print("\nCALL:", call.from_user)
        user_id = call.from_user.id
        bot.edit_message_text("информация о нас", user_id, call.message.message_id, reply_markup=main_key())
    except Exception as e:
        print("\nGET_CALL:", e)


@bot.callback_query_handler(func=lambda call: call.data == "check_order")
def get_call_check_order(call):
    if call.message:
        msg_id = call.message.message_id
    if call.inline_message_id:
        msg_id = call.inline_message_id
    try:

        print("\nCALL FROM_USER:", call.from_user)

        print("\nCALL DATA:", call.data)
        user_id = call.from_user.id

        db_user = DbUser.objects.get(user_id=user_id)

        orders = Order.objects.filter(user=db_user)
        text = ' '
        if orders:
            for order in orders:
                # order.delete()
                text += f'🔸 <b>{order}</b>' + "\n" + "-" * 38 + '\n\n'

                cart = Cart.objects.get(order=order)

                print(cart)
                cart_items = cart.services.all()

                for n, cs in enumerate(cart_items, start=1):
                    title = str(cs).split(" ", maxsplit=1)[-1]
                    text += f"▪️ <b>{n}. {title} - {cs.total_price}</b>" + "\n" + "-" * 38 + '\n'
                    n += 1

                text += f"\n🗓 Дата: {order.lead_time}\n⏱ Время: {order.time_slot}\n" \
                        f"<b>💸 Общая сумма:</b> {cart.total_price} {cart.currency.upper()}" + "\n" + f"ℹ️ Статус: {STATUS.get(order.status)}\n" + "-" * 38 + "\n\n"

            bot.edit_message_text(text, user_id, call.message.message_id)
            bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=check_orders_key(user_id))
        else:
            text = "Забронированных услуг нет."
            bot.edit_message_text(text, user_id, call.message.message_id, reply_markup=main_key())

    except Exception as e:
        print("\nGET_CALL_CHECK_ORDER:", e)


@bot.callback_query_handler(func=lambda call: call.data == "categories")
def get_call(call):
    try:
        print("\nCALL:", call.from_user)
        user_id = call.from_user.id
        bot.delete_message(user_id, call.message.message_id)
        bot.send_message(user_id, "Выберите категорию:", reply_markup=category_key())
    except Exception as e:
        print("\nGET_CALL:", e)


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete:"))
def get_call_delete(call):
    try:

        print("\nCALL:", call.from_user)
        user_id = call.from_user.id

        db_user = DbUser.objects.get(user_id=user_id)
        order_id = call.data.split(":")[-1]
        order = Order.objects.get(user=db_user, id=order_id)

        bot.edit_message_text(f"Вы действительно хотите удалить бронь {order}?",
                              user_id, call.message.message_id, reply_markup=del_order_confirm_key(order_id)
                              )

    except Exception as e:
        print("\nGET_CALL delete:", e)


@bot.callback_query_handler(func=lambda call: call.data.startswith("y_del:"))
def get_call_delete(call):
    try:

        print("\nCALL:", call.from_user)
        user_id = call.from_user.id

        db_user = DbUser.objects.get(user_id=user_id)
        order = Order.objects.filter(user=db_user, id=call.data.split(":")[-1])
        order.delete()

        db_user = DbUser.objects.get(user_id=user_id)

        orders = Order.objects.filter(user=db_user)
        text = ' '
        if orders:
            for order in orders:
                # order.delete()
                text += f'🔸 <b>{order}</b>' + "\n" + "-" * 38 + '\n\n'

                cart = Cart.objects.get(order=order)

                print(cart)
                cart_items = cart.services.all()

                for n, cs in enumerate(cart_items, start=1):
                    title = str(cs).split(" ", maxsplit=1)[-1]
                    text += f"▪️ <b>{n}. {title} - {cs.total_price}</b>" + "\n" + "-" * 38 + '\n'
                    n += 1

                text += f"\n🗓 Дата: {order.lead_time}\n⏱ Время: {order.time_slot}\n" \
                        f"<b>💸 Общая сумма:</b> {cart.total_price} UAH" + "\n" + "-" * 38 + "\n\n"

            bot.edit_message_text(text, user_id, call.message.message_id)
            bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=check_orders_key(user_id))
        else:
            text = "Забронированных услуг нет."
            bot.edit_message_text(text, user_id, call.message.message_id, reply_markup=main_key())

    except Exception as e:
        print("\nGET_CALL del_y:", e)


@bot.callback_query_handler(func=lambda call: call.data == "###")
def get_call(call):
    bot.answer_callback_query(call.id, "Выберите дату")
