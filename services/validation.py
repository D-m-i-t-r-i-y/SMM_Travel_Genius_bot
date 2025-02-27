import re
from datetime import datetime

def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def validate_date_time(date_time):
    try:
        datetime.strptime(date_time, "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False