from tg_bot.loader import bot
from tg_bot.keyboards import services_key
from main.models import Category as Cat
from main.models import Service as Serv

from ..user_data import User, user_dict


@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_id:"))
def get_call(call):
    try:
        print("\nCALL:", call.from_user)
        print("\nCALL DATA:", call.data)
        user_id = call.from_user.id

        try:
            user = user_dict[user_id]
        except:
            user_dict[user_id] = User(user_id)
            user = user_dict[user_id]

        bot.delete_message(user_id, call.message.message_id)
        cat_id = call.data.split(":")[-1]
        user.cat_id = cat_id

        category = Cat.objects.get(id=cat_id)
        users_pagin(user_id, category)
        services = Serv.objects.filter(category=category)[user.pagin[user.n][0]:user.pagin[user.n][1]]
        count = len(services)

        # for n, serv in enumerate(services, start=1):
        text = ''
        for n, s in enumerate(services, 1):
            text += str(n) + ". " + s.title + "\n"

        print("\nTEXT:", text)

        # user.service_count

        textt = f"<b>Категория:</b><i> {category.title}</i>\n\n" \
                f"Выберите услугу:\n\n" + text

        bot.send_message(user_id, textt, reply_markup=services_key(category, user.n, user.pagin), parse_mode="HTML")
    except Exception as e:
        print("\nGET_CALL 'cat_id':", e)


@bot.callback_query_handler(func=lambda call: call.data == "next_serv")
def get_call(call):
    try:
        print("\nCALL:", call.from_user)
        print("\nCALL DATA:", call.data)
        user_id = call.from_user.id

        try:
            user = user_dict[user_id]
        except:
            user_dict[user_id] = User(user_id)
            user = user_dict[user_id]

        bot.delete_message(user_id, call.message.message_id)
        user.n += 1

        category = Cat.objects.get(id=user.cat_id)
        users_pagin(user_id, category)
        services = Serv.objects.filter(category=category)[user.pagin[user.n][0]:user.pagin[user.n][1]]

        # for n, serv in enumerate(services, start=1):
        text = ''
        for n, s in enumerate(services, 1):
            text += str(n) + ". " + s.title + "\n"

        print("\nTEXT:", text)

        # user.service_count

        textt = f"<b>Категория:</b><i> {category.title}</i>\n\n" \
                f"Выберите услугу:\n\n" + text

        bot.send_message(user_id, textt, reply_markup=services_key(category, user.n, user.pagin), parse_mode="HTML")
    except Exception as e:
        print("\nGET_CALL 'next_serv':", e)


@bot.callback_query_handler(func=lambda call: call.data == "prev_serv")
def get_call(call):
    try:
        print("\nCALL:", call.from_user)
        print("\nCALL DATA:", call.data)
        user_id = call.from_user.id

        try:
            user = user_dict[user_id]
        except:
            user_dict[user_id] = User(user_id)
            user = user_dict[user_id]

        bot.delete_message(user_id, call.message.message_id)
        user.n -= 1

        category = Cat.objects.get(id=user.cat_id)
        users_pagin(user_id, category)
        services = Serv.objects.filter(category=category)[user.pagin[user.n][0]:user.pagin[user.n][1]]

        # for n, serv in enumerate(services, start=1):
        text = ''
        for n, s in enumerate(services, 1):
            text += str(n) + ". " + s.title + "\n"

        print("\nTEXT:", text)

        # user.service_count

        textt = f"<b>Категория:</b><i> {category.title}</i>\n\n" \
                f"Выберите услугу:\n\n" + text

        bot.send_message(user_id, textt, reply_markup=services_key(category, user.n, user.pagin), parse_mode="HTML")
    except Exception as e:
        print("\nGET_CALL 'prev_serv':", e)


def users_pagin(user_id, category):
    try:
        user = user_dict[user_id]
    except Exception as e:
        print("text ex:", e)
        user_dict[user_id] = User(user_id)
        user = user_dict[user_id]

    count = len(Serv.objects.filter(category=category))
    # print("COUNT", count)
    page = []
    for i in range(0, count, 6):
        page.append(i)

    user.pagin.clear()
    for i in page:
        x = i + 6
        s = [i, x]
        user.pagin.append(s)
