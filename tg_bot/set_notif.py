import datetime
import os
from crontab import CronTab
from getpass import getuser

cron = CronTab(user=getuser())
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def set_notif(user_id, notif_day, time, order):
    print(BASE_DIR)
    today = datetime.datetime.today()
    print("TODAY", today, notif_day, type(notif_day))
    days = (notif_day - today.date()).days
    print("DAYS", days)
    # h = int(time.split(":")[0])
    h = time.hour
    print(h, today.hour)
    delta = days
    print("DELTA", delta)

    if not delta == 0 and not delta == 1:
        day_before = cron.new(
            command=f'cd {BASE_DIR} && python3 notification.py {user_id} >> ./logs/notification_log.txt',
            comment=str(order))

        day = (today + datetime.timedelta(days=delta))
        print(day)

        months = day.month
        day = day.day
        day_before.hour.on(10)
        day_before.minute.on(0)
        day_before.day.on(day)
        day_before.months.on(months)

        hour_before = cron.new(
            command=f'cd {BASE_DIR} && python3 notification.py {user_id} >> ./logs/notification_log.txt',
            comment=str(order))

        day = (today + datetime.timedelta(days=delta + 1))
        months = day.month
        day = day.day
        # print(type(hour), minute)
        hour_before.hour.on(int(time.hour) - 1)
        hour_before.minute.on(int(time.minute))
        hour_before.day.on(day)
        hour_before.months.on(months)

        cron.write(user=getuser())

    elif not h <= today.hour:
        hour_before = cron.new(
            command=f'cd {BASE_DIR} && python3 notification.py {user_id} hour >> ./logs/notification_log.txt',
            comment=str(order))

        day = (today + datetime.timedelta(days=delta + 1))
        months = day.month
        day = day.day
        # print(type(hour), minute)
        hour_before.hour.on(int(time.hour) - 1)
        hour_before.minute.on(int(time.minute))
        hour_before.day.on(day)
        hour_before.months.on(months)

        cron.write(user=getuser())
