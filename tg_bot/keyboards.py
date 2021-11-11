import datetime
import calendar

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from user_data import month_trans
from main.models import Service as Serv
from main.models import Category as Cat
from main.models import Order as Order
from main.models import User as DbUser
from main.models import Cart
from main.models import Schedule


def payment_key(order):
    key = InlineKeyboardMarkup(row_width=1)

    key.add(
        InlineKeyboardButton(text="Оплатить онлайн", callback_data=f"pay_order:{order.id}"),
        InlineKeyboardButton(text="Наличными", callback_data=f"pay_cash:{order.id}")
    )

    return key


def main_key():
    key = InlineKeyboardMarkup(row_width=1)
    services_btn = InlineKeyboardButton("🚗 Услуги", callback_data="set_auto_type")
    categories_btn = InlineKeyboardButton("🚗 Категории", switch_inline_query_current_chat="Категории")

    express_btn = InlineKeyboardButton('Фулл Контакт', callback_data="express")
    key.add(categories_btn)
    key.add(express_btn)

    key.add(
        InlineKeyboardButton("Проверить бронь", callback_data="check_order"),
        # InlineKeyboardButton('ℹ О нас', callback_data="about")
    )
    return key


def query_service_key(category):
    key = InlineKeyboardMarkup()
    key.add(InlineKeyboardButton("Выбрать услугу", switch_inline_query_current_chat=f'Категория: {category.title}'))
    return key


def query_select_auto_type_key():
    key = InlineKeyboardMarkup()
    key.add(InlineKeyboardButton("Выбрать тип кузова", switch_inline_query_current_chat=f'Тип кузова'))
    return key


def services_key(category, n, pagin):
    key = InlineKeyboardMarkup(row_width=3)
    all_services = Serv.objects.filter(category=category)

    services = Serv.objects.filter(category=category)[pagin[n][0]:pagin[n][1]]

    print("\nSERVICES:", services)
    buttons = []

    for num, serv in enumerate(services, start=1):
        buttons.append(InlineKeyboardButton(f"{num}", callback_data=f"serv_id:{serv.id}"))

        if len(buttons) == len(services) or len(buttons) == 6:
            key.add(*buttons)
            buttons.clear()
    print("len(pagin)", len(pagin), n)
    count = len(pagin) - 1

    if count > n:
        key.add(InlineKeyboardButton("След. ➡️", callback_data="next_serv"))

    if count <= n and n != 0:
        key.add(InlineKeyboardButton("⬅️ Пред.", callback_data="prev_serv"))

    key.add(InlineKeyboardButton("↩️ Категории услуг", callback_data="categories"))
    key.add(InlineKeyboardButton("Ⓜ️ Главное меню", callback_data="main"))

    return key


def category_key():
    key = InlineKeyboardMarkup(row_width=1)
    categories = Cat.objects.all()
    print("\nCATEGORIES:", categories)
    buttons = []

    for cat in categories:
        buttons.append(InlineKeyboardButton(f"➡️ {cat.title}", callback_data=f"cat_id:{cat.id}"))

        if len(buttons) == len(categories):
            key.add(*buttons)
            buttons.clear()

    key.add(InlineKeyboardButton("Ⓜ️ Главное меню", callback_data="main"))

    return key


def serv_key(service, cart=None):
    key = InlineKeyboardMarkup(row_width=1)
    key.add(InlineKeyboardButton("➕ Добавить услугу в корзину", callback_data=f"add_to_cart:{service.id}"))
    if cart:
        key.add(InlineKeyboardButton("🛍 Оформить заказ", callback_data=f"set_date_order:{cart.id}"))

    key.add(InlineKeyboardButton("🚗 Категории", switch_inline_query_current_chat="Категории"))
    key.add(InlineKeyboardButton("Корзина", callback_data="n_cs_del"))
    key.add(InlineKeyboardButton("Ⓜ️ Главное меню", callback_data="main"))

    return key


def checkout(cart_id):
    key = InlineKeyboardMarkup()
    cart_services = Cart.objects.filter(id=cart_id).first().services.all()
    added_buttons = []

    for n, cs in enumerate(cart_services, start=1):
        added_buttons.append(InlineKeyboardButton(f"❌{n}", callback_data=f"del_cs:{cs.id}"))
        if len(added_buttons) == len(cart_services):
            key.add(*added_buttons)
            added_buttons.clear()

    key.add(InlineKeyboardButton("➕ Добавить услуги", switch_inline_query_current_chat=f"Категории"))
    if cart_services:
        key.add(InlineKeyboardButton("🛍 Оформить заказ", callback_data=f"set_date_order:{cart_id}"))
    key.add(InlineKeyboardButton("Ⓜ️ Главное меню", callback_data="main"))
    return key


def choice_time_key(cart_id, date):
    key = InlineKeyboardMarkup()
    tt = datetime.datetime.now().time().strftime("%H:%M:%S")
    check_date = datetime.datetime.strptime(date, "%d %m %Y").date()

    a = datetime.datetime.now()
    check_t = a.time()
    if check_date > a.date():
        check_t = datetime.datetime.strptime("8:00", "%H:%M").time()
    time_slots = []
    try:
        schedule_date = Schedule.objects.filter(date=datetime.date.today()).first().rel_time.all()
        for t in schedule_date:
            print(t, t.time < check_t)
            if t.time > check_t:
                if str(t).startswith("0"):
                    t = str(t)[1:]
                time_slots.append(str(t))
    except Exception as e:
        print(e)

        schedule_date = Schedule.objects.get(title="По умолчанию").rel_time.all()
        for t in schedule_date:
            check = t.time < check_t
            print(t, check)

            if not check:
                time_slots.append(str(t))

            else:
                if str(t).startswith("0"):
                    t = str(t)[1:]
                    time_slots.append(str(t))

    print(check_date)

    orders = Order.objects.filter(lead_time=check_date)

    buttons = []
    key.add(InlineKeyboardButton("Изменить дату", callback_data=f"set_date_order:{cart_id}"))

    print(orders)
    for order in orders:
        print("order.time_slot:", order.time_slot)
        if order.time_slot in time_slots:
            try:
                time_slots.remove(order.time_slot)
            except Exception as e:
                print("rm ex", e)

    for n, time in enumerate(time_slots):
        buttons.append(InlineKeyboardButton(f"{time}", callback_data=f"order_time-{time}"))
        if len(buttons) > 1:
            key.add(*buttons)
            buttons.clear()

    key.add(InlineKeyboardButton("Ⓜ️ Главное меню", callback_data="main"))

    return key


def change_cart():
    key = InlineKeyboardMarkup()
    key.add(InlineKeyboardButton("Изменить заказ", callback_data="n_cs_del"))

    return key


def add_comment_key(cart_id, order_date):
    key = InlineKeyboardMarkup()
    key.add(InlineKeyboardButton("✏️ Изменить дату", callback_data=f"set_date_order:{cart_id}"))
    key.add(InlineKeyboardButton("✏️ Изменить время",
                                 callback_data=f"order:{cart_id}_date:{order_date.strftime('%d %m %Y')}")),
    key.add(InlineKeyboardButton("Изменить заказ", callback_data="n_cs_del"))

    key.add(InlineKeyboardButton("📝 Добавить комментарий", callback_data="add_comment"))
    key.add(InlineKeyboardButton("✅ Подтвердить заказ", callback_data="confirm_order"))

    key.add(InlineKeyboardButton("Ⓜ️ Главное меню", callback_data="main"))

    return key


def return_key():
    key = ReplyKeyboardMarkup(True, False)
    key.row('↩️ Вернуться')
    return key


def phone_request_key():
    key = ReplyKeyboardMarkup(True, True)
    key.add(KeyboardButton("Отправить номер телефона", request_contact=True))
    return key


def set_auto_type_key():
    key = InlineKeyboardMarkup(row_width=1)

    key.add(
        InlineKeyboardButton("Седан", callback_data="auto:sedan"),
        InlineKeyboardButton("Хетчбэк", callback_data="auto:hatchback"),
        InlineKeyboardButton("Внедорожник", callback_data="auto:jeep"),
    )
    key.add(InlineKeyboardButton("Ⓜ️ Главное меню", callback_data="main"))

    return key


def check_orders_key(user_id):
    key = InlineKeyboardMarkup(row_width=2)

    db_user = DbUser.objects.get(user_id=user_id)
    orders = Order.objects.filter(user=db_user, related_cart__in_order=True)
    for n, o in enumerate(orders, 1) :
        if o.status == '0':
            key.add(
                InlineKeyboardButton(f"❌ {n}. Заказ № {o.id}", callback_data=f"delete:{o.id}")
            )
        else:
            key.add(
                InlineKeyboardButton(f"✅ {n}. Заказ № {o.id}", callback_data=f"x")
        )
    key.add(InlineKeyboardButton("Ⓜ️ Главное меню", callback_data="main"))

    return key


def del_order_confirm_key(order_id):
    key = InlineKeyboardMarkup(row_width=1)

    key.add(
        InlineKeyboardButton("Да", callback_data=f"y_del:{order_id}"),
        InlineKeyboardButton("Нет", callback_data="check_order")
    )

    return key


def del_cs_confirm_key(cs_id):
    key = InlineKeyboardMarkup(row_width=1)

    key.add(
        InlineKeyboardButton("Да", callback_data=f"y_cs_del:{cs_id}"),
        InlineKeyboardButton("Нет", callback_data="n_cs_del")
    )

    return key


def calendar_(cart_id):
    key = InlineKeyboardMarkup(row_width=7)
    month = calendar.TextCalendar(calendar.MONDAY)
    today = datetime.datetime.today()

    print(month.firstweekday, month.getfirstweekday)
    month_days = month.itermonthdays(today.year, today.month)

    week_days = ['ПН', "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]  # key.add(InlineKeyboardButton())
    day_buttons = []
    date_btns = []

    month_btn = InlineKeyboardButton(month_trans.get(str(today.month)).get("ru"), callback_data="###")
    key.add(month_btn)
    for w in week_days:
        day_buttons.append(InlineKeyboardButton(w, callback_data="###"))

        if len(day_buttons) == 7:
            key.add(*day_buttons)
            day_buttons.clear()

    for d in month_days:
        day = d
        c_data = f"order:{cart_id}_date:{d} {today.month} {today.year}"

        if d == 0:
            d = " "
            date_btns.append(InlineKeyboardButton(f"{d}", callback_data="###"))

        else:
            if int(d) < int(today.day):
                c_data = "###"
            if int(d) == int(today.day):
                day = f"[{d}]"
            date_btns.append(InlineKeyboardButton(day, callback_data=c_data))

        if len(date_btns) == 7:
            key.add(*date_btns)
            date_btns.clear()
    return key


def users_orders_key(user_id):
    key = InlineKeyboardMarkup()

    orders = Order.objects.filter(user__user_id=user_id)
    for order in orders:
        text = " "
        print(order.status)
        title = str(order).split("Клиент")[0]

        status = " "

        if order.sent:
            status = "✅"
        if str(order.status) == "3":
            status = "⌛️"
        if order.status == "1":
            status = "⌛️"

        text += (title + " " + order.status + status).strip()
        key.add(
            InlineKeyboardButton(title, callback_data=f"user_order:{order.id}"),
        )

    return key
