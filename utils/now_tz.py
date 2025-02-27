from datetime import datetime
import pytz
from config import TZ

# Создать время в UTC

def now_tz(tz = TZ):
    # Конвертировать в другой часовой пояс (например, Нью-Йорк)
    now_time = datetime.now(pytz.utc).astimezone(pytz.timezone(tz))
    return now_time


if __name__ == '__main__':
    print(now_tz(TZ))