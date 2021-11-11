import os

from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.checks import messages
from django.db import models
from django.forms import TextInput, Textarea, NumberInput
from django.utils.safestring import mark_safe
from sorl.thumbnail import get_thumbnail
from telebot.types import InputMediaPhoto

from .notification import bot
from .models import *
from avto_admin.settings import BASE_DIR


class TimeSlotInline(admin.TabularInline):
    model = TimeSlot


class CartInline(admin.TabularInline):
    model = Cart
    extra = 0
    # fields = ['services', ]
    exclude = ['user', 'in_order', 'total_services', 'for_anon_user']

    readonly_fields = ['total_price', 'get_total_price']
    can_delete = False

    fieldsets = [
        (None, {
            'fields': (('services',), 'total_price',)
        }),
    ]

    def get_total_price(self, request, obj=None):
        print(obj)
        if obj.related_cart:
            res = mark_safe(f"<strong>{obj.related_cart.get(order=obj).total_price} #</strong>")
            print(res)
            return res

    get_total_price.shirt_description = 'Цена'

    def has_add_permission(self, request, obj=None):
        print(obj, obj.related_cart.get(order=obj))

        return False

    def has_delete_permission(self, request, obj=None):
        return False


class UserServiceInline(admin.TabularInline):
    model = UserService

    extra = 0


class UserAutoInline(admin.TabularInline):
    model = Auto
    extra = 0


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    save_on_top = True

    list_display = ["first_name", "last_name", "phone_number", "username", ]
    list_display_links = ["first_name", "last_name", ]
    readonly_fields = ["first_name", "last_name", "phone_number", "username", 'user_id', ]
    search_fields = ["first_name", "last_name", "phone_number", "username", ]
    fieldsets = (

        ("Info", {
            "fields": (("first_name", "last_name"),)
        }),

        ("Telegram", {
            "fields": ("username", "user_id")
        }),
        ("Контакты:", {
            "fields": ("phone_number",)
        }),
        ("Адрес:", {
            "fields": ("address",)
        }),

    )

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '40'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 130})},
        models.IntegerField: {'widget': NumberInput(attrs={'size': "13"})},
    }
    inlines = [UserAutoInline, ]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    save_on_top = True

    list_display = ['title', 'price', 'category']
    list_display_links = ['title', ]
    list_filter = ['category', ]
    search_fields = ['title']

    fieldsets = (

        (None, {
            "fields": (("title",), "category",)
        }),
        ("детали", {
            "fields": ("description",)
        }),
        ("Цены", {
            "fields": (("price", "currency"), ('price_low', 'price_mid', 'price_high'))
        }),

    )
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '90'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 130})},
        models.IntegerField: {'widget': NumberInput(attrs={'size': "13"})},
    }


@admin.register(Auto)
class AutoAdmin(admin.ModelAdmin):
    save_on_top = True

    list_display = ['brand', 'brand_model', 'auto_class', 'fuel_type', 'owner']
    list_display_links = ['brand', ]
    list_filter = ['auto_class', 'fuel_type']
    search_fields = ['brand', 'brand_model', 'auto_class', 'fuel_type', 'owner']

    fieldsets = (

        (None, {
            "fields": (("brand", "brand_model", 'year'),)
        }),
        (None, {
            "fields": (("auto_class", "fuel_type"),)
        }),
        (None, {
            "fields": ("owner",)
        }),

    )

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '20'})},
    }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    save_on_top = True

    list_display = ['title', ]
    list_display_links = ['title', ]
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ['id', 'user', 'auto_type', 'status', 'get_total_price', 'lead_time', "time_slot", "sent"]
    list_filter = ['lead_time', 'status', ]
    readonly_fields = ['created', ]

    inlines = [CartInline, ]
    # AddCartInline
    fieldsets = (

        (None, {
            "fields": (("user",),)
        }),

        (None, {
            "fields": (('status', "time_slot", "lead_time",), "auto_type",)
        }),

        (None, {
            "fields": ("comment",)
        }),
        (None, {
            "fields": ("created",)
        }),
        ("фотоотчет", {
            "fields": (("image",), "message")
        }),
    )

    def get_comment(self, obj):
        if obj.comment:
            return obj.comment[:30]
        else:
            return "-"

    def get_total_price(self, obj):
        if obj.related_cart:
            return mark_safe(f"<strong>{obj.related_cart.first().total_price} UAH</strong>")

    get_comment.short_description = 'Комм.'
    get_total_price.short_description = 'Сумма заказа'

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '100'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 130})},

    }

    actions = ['send_post']

    def send_post(self, requsest, queryset):
        try:
            media = []
            print(queryset)
            for post in queryset:
                print(type(post))
                text = f"{str(post).split('Клиент')[0]} - Выполнен.\n"
                text += post.message
                # photo_path = os.path.join(BASE_DIR) + images[0].image.url
                # image = get_thumbnail(post.image, '1000x1000', crop='center', quality=99)

                photo_path = os.path.join(BASE_DIR) + post.image.url

                print("PHOTO_PATH", photo_path)
                with open(photo_path, 'rb') as file:
                    media.append(InputMediaPhoto(file, caption=text))

                    # bot.send_photo(445116305, file, caption=post.text)
                    bot.send_media_group(post.user.user_id, media)

                    post.sent = True
                    post.save()
                    self.message_user(requsest, message=f"Отчет: {post} отправлен.")

        except Exception as e:
            print("send_post ex:", e)
            self.message_user(requsest, message=f"Отчет {post} не отправлен - {e}", level=messages.ERROR)
            post.sent = False
            post.save()

    send_post.short_description = 'Отправить'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ['id', 'user', 'order']
    search_fields = ['user', 'order']


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ['title', 'date']
    list_display_links = ['title']
    search_fields = ['title', 'date']

    inlines = [TimeSlotInline]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'username', 'user_id']


admin.site.unregister(Group)
admin.site.site_title = "Панель администратора"
admin.site.site_header = "Панель администратора"
admin.site.site_url = "/admin"
