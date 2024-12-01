import telebot
import requests
from telebot import types
import re

TOKEN = '7598029898:AAGm7by_L2HvH86e5_-kmkEhhNj_x8y_nRA'
IPINFO_TOKEN = '511a0ee61b7f2f'  # Токен для ipinfo.io
bot = telebot.TeleBot(TOKEN)

# Флаг для отслеживания первого запуска
first_start = True

def is_valid_ip(ip):
    # Регулярное выражение для проверки формата IP-адреса
    pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
    return re.match(pattern, ip) is not None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    global first_start
    if first_start:
        welcome_text = (
            "*Привет!*\n"
            "Я бот для получения информации о IP-адресах.\n"
            "Вот что я могу сделать:\n"
            "- Получить подробную информацию о любом IP-адресе.\n"
            "- Ответить на ваши вопросы о ботах.\n\n"
            "Вы можете поддержать меня, нажав кнопку 'Донат' ниже.\n"
            "После первого использования, для перезапуска просто отправьте команду /start."
        )
        markup = types.InlineKeyboardMarkup()
        donate_button = types.InlineKeyboardButton("Донат", url="https://www.donationalerts.com/r/squate_dev")
        markup.add(donate_button)
        bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=markup)
        first_start = False  # Устанавливаем флаг, чтобы не показывать это сообщение снова
    else:
        bot.reply_to(message, "Добро пожаловать обратно! Чтобы получить информацию о IP-адресе, отправьте мне его.")

@bot.message_handler(commands=['shutdown'])
def shutdown_bot(message):
    bot.reply_to(message, "*Бот отключен.*", parse_mode='Markdown')
    print("Бот отключен.")  # Сообщение в консоль
    exit()  # Отключаем бота

@bot.message_handler(func=lambda message: True)
def get_ip_info(message):
    ip_address = message.text.strip()
    
    if not ip_address:
        bot.reply_to(message, "*Пожалуйста, введите IP-адрес.*", parse_mode='Markdown')
        return

    if not is_valid_ip(ip_address):
        bot.reply_to(message, "*Некорректный формат IP-адреса. Пожалуйста, введите действительный IP-адрес.*", parse_mode='Markdown')
        return

    try:
        response = requests.get(f"https://ipinfo.io/{ip_address}/json?token={IPINFO_TOKEN}")
        
        if response.status_code == 200:
            data = response.json()
            if 'error' not in data:
                loc = data.get('loc', 'Неизвестно').split(',')
                latitude = loc[0] if len(loc) > 0 else 'Неизвестно'
                longitude = loc[1] if len(loc) > 1 else 'Неизвестно'

                info = (
                    f"*IP:* `{data.get('ip', 'Неизвестен')}`\n"
                    f"*Страна:* `{data.get('country', 'Неизвестна')}`\n"
                    f"*Регион:* `{data.get('region', 'Неизвестен')}`\n"
                    f"*Город:* `{data.get('city', 'Неизвестен')}`\n"
                    f"*Почтовый индекс:* `{data.get('postal', 'Неизвестен')}`\n"
                    f"*Широта:* `{latitude}`\n"
                    f"*Долгота:* `{longitude}`\n"
                    f"*ISP:* `{data.get('org', 'Неизвестен')}`\n"
                    f"*Hostname:* `{data.get('hostname', 'Неизвестен')}`\n"
                    f"*Временная зона:* `{data.get('timezone', 'Неизвестна')}`\n"
                    f"*Тип соединения:* `{data.get('connection', 'Неизвестно')}`\n"
                    f"*Атрибуция:* `{data.get('abuse', 'Неизвестна')}`\n"
                    f"*Расположение:* `{data.get('location', 'Неизвестно')}`\n"
                    f"*Код страны:* `{data.get('country', 'Неизвестен')}`\n"
                    f"*Код телефона:* `{data.get('country', 'Неизвестен')}`\n"
                    f"*Дата создания:* `{data.get('created', 'Неизвестно')}`\n"
                    f"*Обновлено:* `{data.get('updated', 'Неизвестно')}`\n"
                    f"*Сетевой оператор:* `{data.get('org', 'Неизвестен')}`\n"
                )
                bot.reply_to(message, info, parse_mode='Markdown')
            else:
                bot.reply_to(message, "*Не удалось получить информацию об этом IP-адресе.*", parse_mode='Markdown')
        else:
            bot.reply_to(message, "*Произошла ошибка при обращении к API.*", parse_mode='Markdown')

    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"*Произошла ошибка при запросе: {str(e)}*", parse_mode='Markdown')

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен.")
    bot.polling()
