# [file name]: services/email_service.py V0->v2
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import json
import logging
from config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FIXED_EMAIL
import aiofiles
import uuid
import inspect

logger = logging.getLogger(__name__)


async def send_email(user_data, image_path):
    """Асинхронная отправка статьи с изображением через Yandex"""
    func_name = inspect.currentframe().f_code.co_name
    logging.info(f"\n\n[{func_name}]:"
                 f"\nДанные: {user_data}"
                 f"\nКартинка: {image_path}"
                 )
    try:
        msg = MIMEMultipart()
        msg['Subject'] = (f"Travel Blog Post into group {user_data['telegram_group']} | "
                          f"at {user_data['schedule_time']} |"
                          f"Topic {user_data['destination']} "
                          f"{user_data['selected_title']}"
                         )

        msg['From'] = SMTP_USER
        msg['To'] = FIXED_EMAIL

        # Обязательная текстовая часть
        text_content = (
            f"{user_data['selected_title']}\n\n"
            f"{user_data['content']}"
            # f"Детали публикации:\n"
            # f"Дата: {user_data['schedule_time']}\n"
            # f"Группа: {user_data['telegram_group']}\n"
            # f"Тема: {user_data['topic']}\n"
            # f"Заголовок: {user_data['selected_title']}\n"
        )
        msg.attach(MIMEText(text_content, 'plain', 'utf-8'))

        # JSON-вложение как файл
        #json_data = json.dumps(user_data, ensure_ascii=False, indent=2).encode('utf-8')
        #json_part = MIMEApplication(json_data, Name="article_data.json")
        #json_part['Content-Disposition'] = 'attachment; filename="article_data.json"'
        #msg.attach(json_part)

        # Изображение
        async with aiofiles.open(image_path, "rb") as f:
            image_data = await f.read()
        image_part = MIMEImage(image_data)
        image_part.add_header('Content-Disposition', 'attachment', filename=f"image_{uuid.uuid4()}.jpg")
        msg.attach(image_part)

        # Отправка через Yandex SMTP
        await aiosmtplib.send(
            msg,
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
            use_tls=True,
            start_tls=(SMTP_PORT == 587)  # Для порта 587
        )
        logger.info("Письмо успешно отправлено!")
        return True

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return False


async def send_user_report(email, user_data):
    """Отправка отчета пользователю"""
    try:
        msg = MIMEMultipart()
        msg['Subject'] = "Ваш пост запланирован: {}: {} ".format(user_data['destination'], user_data['selected_title'])
        msg['From'] = SMTP_USER
        msg['To'] = email

        # Текст + HTML-версия (опционально)
        text = f"Пост '{user_data['destination']}: {user_data['selected_title']}' будет опубликован {user_data['schedule_time']}."
        html = f"""<html><body>
            <p>Пост <strong>{user_data['destination']}</strong> будет опубликован {user_data['schedule_time']}.</p>
        </body></html>"""

        msg.attach(MIMEText(text, 'plain', 'utf-8'))
        msg.attach(MIMEText(html, 'html', 'utf-8'))

        await aiosmtplib.send(
            msg,
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
            use_tls=True
        )
        logger.info("Отчет отправлен пользователю")
        return True

    except Exception as e:
        logger.error(f"Ошибка отчета: {str(e)}")
        return False