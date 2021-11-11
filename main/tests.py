import calendar
from datetime import datetime
from django.test import TestCase

# Create your tests here.
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def calendar_():
    key = InlineKeyboardMarkup(row_width=7)
    month = calendar.TextCalendar(calendar.MONDAY)
    month_days = month.itermonthdays(2021, 2)
    week_days = ['ПН', "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
    n = 0
    cal = []
    some = []
    dicts = {}
    for d in month_days:
        for w in week_days:
            cal.append(dict(day=w, date=d))
        if n == 7:
            some.append(cal)
            cal.clear()

            n = 0
            continue
        n += 1

    print(some)
    key.add(InlineKeyboardButton('ПН', ))


calendar_()
"""думаю тогда стоит созвониться , обсуждать проект,обсудить и вместе составить план и задания в jira, заодно разобраться с сервисом, я там создал проект и несколько задач"""