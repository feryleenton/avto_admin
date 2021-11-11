class User:
    order_comment = "-"

    def __init__(self, user_id, order_comment=None, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.user_id = user_id
        self.order_comment = order_comment
        self.n = 0
        self.pagin = []


class UserOrder:
    user_id = 0

    def __init__(self, user_id, *args, **kwargs):
        super(UserOrder, self).__init__(*args, **kwargs)
        self.user_id = user_id


user_dict = {}


def get_user_data(user_id):
    try:

        user = user_dict[user_id]
        return user

    except Exception as e:
        print("GET_USER_DATA ex:", e)
        user_dict[user_id] = User(user_id)
        user = user_dict[user_id]

        return user


auto_types = {"sedan": 'Седан',
              "hatchback": "Хетчбэк",
              "jeep": "Внедорожник",
              "universal": "Универсал",
              "minivan": "Минивэн",
              "microavtobus": "Микроавтобус",
              "crossover": "Кроссовер",
              "malolitraj": "Малолитражный",
              'pickup': 'Пикап',
              'coupe': 'Купе',
              'van': 'Фургон'}

month_trans = {"1": {"ru": "Январь", "ua": "Січень"},
               "2": {"ru": "Февраль", "ua": "Лютый"},
               "3": {"ru": "Март", "ua": "Березень"},
               "4": {"ru": "Апрель", "ua": "Квітень"},
               "5": {"ru": "Май", "ua": "Травень"},
               "6": {"ru": "Июнь", "ua": "Червень"},
               "7": {"ru": "Июль", "ua": "Липень"},
               "8": {"ru": "Август", "ua": "Серпень"},
               "9": {"ru": "Сентябрь", "ua": "Вересень"},
               "10": {"ru": "Октябрь", "ua": "Жовтень"},
               "11": {"ru": "Ноябрь", "ua": "Листопад"},
               "12": {"ru": "Декабрь", "ua": "Грудень"},
               }
