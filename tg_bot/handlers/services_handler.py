from tg_bot.loader import bot
from tg_bot.keyboards import serv_key
from main.models import Service as Serv


@bot.callback_query_handler(func=lambda call: call.data.startswith("serv_id:"))
def get_call(call):
    print("\nCALL:", call.from_user)
    print("\nCALL DATA:", call.data)
    try:
        print("\nCALL:", call.from_user)
        print("\nCALL DATA:", call.data)
        user_id = call.from_user.id
        bot.delete_message(user_id, call.message.message_id)
        serv_id = call.data.split(":")[-1]
        service = Serv.objects.get(id=serv_id)
        bot.send_message(user_id, f"<b>{service.title}</b>\n\n"
                                  f"<b>Описание услуги:</b><i> {service.description}</i>\n\n"
                                  f"<b>Стоимость:</b> <i>{service.price}</i>",
                         reply_markup=serv_key(service), parse_mode="HTML")
    except Exception as e:
        print("\nGET_CALL 'cat_id':", e)