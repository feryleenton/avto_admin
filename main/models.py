from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe


class Category(models.Model):
    title = models.CharField(max_length=100, verbose_name="Название категории", null=True)
    show = models.BooleanField(verbose_name="Доступна", default=False)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Service(models.Model):
    CURRENCY = (
        ('usd', 'USD'),
        ('eur', 'EUR'),
        ('rub', 'RUB'),
        ('uah', 'UAH'),

    )
    title = models.CharField(max_length=100, verbose_name="Название услуги", null=True)

    description = models.TextField(max_length=1024, verbose_name="Описание услуги", null=True, blank=True,
                                   default="Не указано")

    image = models.ImageField(verbose_name='Фото услуги', upload_to="service_photo/", null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена', null=True, default=0, blank=True)
    currency = models.CharField(max_length=20, verbose_name="Валюта", null=True, choices=CURRENCY, default='uah')
    price_low = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена кат. 1', null=True, default=0, blank=True)
    price_mid = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена кат. 2', null=True, default=0, blank=True)
    price_high = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена кат. 3', null=True, default=0, blank=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, verbose_name="Категория")

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"


class User(models.Model):
    user_id = models.IntegerField(verbose_name="user_id", blank=True, null=True)
    username = models.CharField(verbose_name="Имя пользователя", max_length=255, blank=True, null=True)

    first_name = models.CharField(max_length=100, verbose_name="Имя", blank=True, null=True)
    last_name = models.CharField(max_length=100, verbose_name="Фамилия", blank=True, null=True)

    phone_number = models.BigIntegerField(verbose_name="Номер телефона", blank=True, null=True)

    address = models.CharField(verbose_name="Адрес", blank=True, max_length=255, null=True)
    # auto = models.CharField(max_length=100, verbose_name="Автомобиль", null=True, blank=True)
    auto_number = models.CharField(max_length=100, verbose_name="Номер авто", null=True, blank=True)

    autos = models.ManyToManyField('Auto', verbose_name="авто", related_name="users_autos", blank=True)
    # orders = models.ManyToManyField('self', through='Orders', symmetrical=False)
    auto = models.ForeignKey('Auto', verbose_name='avto', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"


class Auto(models.Model):
    AUTO_TYPE = (
        ("sedan", 'Седан'),
        ("hatchback", "Хетчбэк"),
        ("jeep", "Внедорожник"),
        ("universal", "Универсал"),
        ("minivan", "Минивэн"),
        ("microavtobus", "Микроавтобус"),
        ("crossover", "Кроссовер"),
        ("malolitraj", "Малолитражный"),
        ('pickup', 'Пикап'),
        ('coupe', 'Купе'),
        ('van', 'Фургон'),

    )
    FUEL_TYPE = (
        ("petrol", "Бензин"),
        ("diesel", "Дизель"),
        ("gas_petrol", "Газ/Бензин"),
        ("gas", "Газ"),
        ('electric', 'Электро')

    )
    brand = models.CharField(max_length=100, verbose_name="Марка", null=True)
    brand_model = models.CharField(max_length=100, verbose_name="Модель", null=True, blank=True)

    auto_class = models.CharField(max_length=100, verbose_name="Тип кузова", null=True, choices=AUTO_TYPE,
                                  default='sedan')
    year = models.PositiveSmallIntegerField(verbose_name='Год выпуска', null=True, blank=True)
    fuel_type = models.CharField(max_length=20, verbose_name='Тип топлива', null=True, choices=FUEL_TYPE,
                                 default='petrol')
    number = models.CharField(max_length=20, verbose_name="Гос. номер", null=True, blank=True)
    owner = models.ForeignKey(User, related_name='user_auto', verbose_name='Владелец', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.brand}"

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'


class Order(models.Model):
    AUTO_TYPE = (
        ("sedan", 'Седан'),
        ("hatchback", "Хетчбэк"),
        ("jeep", "Внедорожник")

    )

    STATUS = (
        ("0", "Заявка"),
        ("1", "Забронирован"),
        ('2', 'Оплачен'),
        ("3", "Выполняется"),
        ("4", "Выполнен")
    )

    TIME_SLOT = (
        ('9:30', '9:30'),
        ('10:30', '10:30'),
        ('12:00', '12:00'),
        ('12:30', '12:30'),
        ('13:00', '13:00'),
        ('15:00', '15:00'),
        ('15:30', '15:30'),
        ('16:00', '16:00'),
        ('17:00', '17:00'),
        ('18:00', '18:00'),
        ('18:30', '18:30'),
    )
    user = models.ForeignKey(User, verbose_name="Клиент", on_delete=models.CASCADE)

    comment = models.TextField(verbose_name="Комментарий", null=True, blank=True)
    # time_slot = models.CharField(max_length=25, verbose_name="Время", null=True, choices=TIME_SLOT, blank=True, default=None)
    time_slot = models.TimeField(verbose_name='Время', null=True, blank=True)
    created = models.DateTimeField(verbose_name="время создания заказа", auto_now_add=True, null=True)
    lead_time = models.DateField(verbose_name="дата выполнения заказа", default=timezone.now, null=True, blank=True)

    # status = models.BooleanField(verbose_name="Статус", default=False)
    status = models.CharField(verbose_name="Статус", max_length=255, choices=STATUS, default='0')

    auto_type = models.CharField(verbose_name='тип авто', max_length=50, choices=AUTO_TYPE, null=True, blank=True)
    image = models.ImageField(verbose_name='Фото отчет', upload_to="service_photo/", blank=True, null=True)
    # check = models.
    sent = models.BooleanField(verbose_name="отчет", default=False, blank=True)

    message = models.TextField(max_length=4096, verbose_name="Сообщение", null=True, blank=True)
    confirmed = models.BooleanField(verbose_name="подтвержден", default=False, blank=True)

    def __str__(self):
        # return f"Заказ № {self.id} {self.user} | {self.service}"
        return f"Заказ № {self.id} Клиент: {self.user}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class UserAuto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auto = models.ForeignKey(Auto, on_delete=models.CASCADE)


class UserService(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)


class CartService(models.Model):
    user = models.ForeignKey(User, verbose_name='Клиент', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', related_name='related_services', on_delete=models.CASCADE,
                             null=True)

    service = models.ForeignKey(Service, verbose_name='Услуга', on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)
    currency = models.CharField(max_length=20, verbose_name='Валюта', null=True, blank=True)
    total_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена', null=True, default=0)

    def __str__(self):
        return f"{self.id} {self.service}"

    class Meta:
        verbose_name = 'CartService'
        verbose_name_plural = "CartServices"


class Cart(models.Model):
    user = models.ForeignKey(User, verbose_name='Клиент', on_delete=models.CASCADE)
    services = models.ManyToManyField(CartService, related_name='related_cart', verbose_name='Услуги', blank=True)

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='related_cart', null=True,
                              verbose_name='Заказ', blank=True)

    total_services = models.PositiveIntegerField(default=0)

    total_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена', default=0)
    currency = models.CharField(max_length=20, verbose_name='Валюта', null=True, blank=True)
    in_order = models.BooleanField(default=False)

    def __str__(self):
        return f"Корзина №: {self.id} Клиент: {self.user}"

    @classmethod
    def get_total_price(cls):
        if cls.total_price:
            return mark_safe(f"<strong>{cls.total_price} рублей</strong>")

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = "Корзины"


class Schedule(models.Model):
    title = models.CharField(max_length=100, verbose_name="Название", null=True)
    date = models.DateField(verbose_name='Дата', blank=True, null=True)

    # time = models.ManyToManyField('TimeSlot', verbose_name="Время", related_name="rel_schedule")

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = "Расписания"


class TimeSlot(models.Model):
    date = models.ForeignKey(Schedule, related_name="rel_time", on_delete=models.CASCADE)
    time = models.TimeField(verbose_name="Время")

    def __str__(self):
        return str(self.time)[:5]

    class Meta:
        verbose_name = 'Время'


class Notification(models.Model):
    user_id = models.IntegerField(verbose_name="user_id", editable=False, null=True, blank=True)
    username = models.CharField(max_length=255, verbose_name="Имя пользователя", null=True, editable=False)
    phone_number = models.CharField(max_length=20, verbose_name="Телефон", null=True)

    def __str__(self):
        return f"{self.username}"

    class Meta:
        verbose_name = 'Оповещение'
        verbose_name_plural = 'Оповещения'