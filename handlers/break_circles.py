import json
import pytz
from datetime import datetime, timedelta
import logging
from config import TZ

def load_config(user_id: int) -> dict:
    try:
        with open("user_configs.json", "r") as f:
            configs = json.load(f)
            user_config = configs.get(str(user_id), {})

            # Генерация времени по умолчанию, если его нет
            if "schedule_time" not in user_config:
                timezone = pytz.timezone(TZ)  # Указываем нужный часовой пояс
                # время в будущем (минимум на 5 минут вперед)
                user_config["schedule_time"] = (datetime.now(timezone) + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
            if "group_id" in user_config:
                user_config["group_id"] = str(user_config["group_id"])

            return user_config
    except FileNotFoundError:
        return {"schedule_time": (datetime.now() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")}

def save_config(user_id: int, data: dict):
    try:
        with open("user_configs.json", "r") as f:
            configs = json.load(f)
    except FileNotFoundError:
        configs = {}

    configs[str(user_id)] = data

    try:
        with open("user_configs.json", "w") as f:
            json.dump(configs, f, indent=4)
    except Exception as e:
        logging.error(f"Ошибка сохранения конфига: {e}")
        raise