import telebot, requests
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
# Инициализация бота и базы данных 
bot = telebot.TeleBot("your token")
user_sessions = {}  # Тут храняться сессии пользователей

# Основное меню
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Играть"),
               KeyboardButton("Список лидеров"),
               KeyboardButton("Зарегистрироваться"),
               KeyboardButton("Войти"),
               KeyboardButton("Выйти"))
    return markup

# Обработчик команды /start
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "Добро пожаловать в ShyrikFnaf. Чего вы изволите?",
        reply_markup=main_menu()
    )
    
# Запуск игры
@bot.message_handler(func=lambda message: message.text == "Играть")
def game_start(message):
    session = user_sessions.get(message.chat.id, {})
    if session.get("In_ac", True):
        try:
            # Отправка игрового файла
            with open("test.zip", "rb") as file:
                bot.send_document(message.chat.id, file, caption="Лаунчер для скачивания игр.")
        except FileNotFoundError:
            bot.send_message(message.chat.id, "Файл с лаунчером не найден.")
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка: {e}")
    else:
        bot.send_message(message.chat.id, "Зайдите в учётную запись!")

# Регистрация пользователя
@bot.message_handler(func=lambda message: message.text == "Зарегистрироваться")
def add_user_handler(message):
    session = user_sessions.get(message.chat.id, {})
    if not session.get("In_ac", False):
        bot.send_message(message.chat.id, "Введите имя пользователя и пароль через запятую (например: Иван, 1234):")
        bot.register_next_step_handler(message, register_user)
    else:
        bot.send_message(message.chat.id, "Вы уже вошли в учётную запись.")

def register_user(message):
    try:
        name, password = map(str.strip, message.text.split(","))

        user_data = requests.get(f"https://asmoraks.pythonanywhere.com/api/register/{name}/{password}")
        user_data = user_data.json()
        if user_data["status"] == "success":
            bot.send_message(message.chat.id, f"Пользователь с именем '{name}' успешно зарегистрирован!")
            user_sessions[message.chat.id] = {"In_ac": True, "user": user_data["user_name"] and user_data["user_id"]}
        else:
            bot.send_message(message.chat.id, "Ошибка! Пользователь с таким именем уже зарегистрирован.")
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка! Убедитесь, что вы ввели имя и пароль через запятую.")

# Авторизация пользователя
@bot.message_handler(func=lambda message: message.text == "Войти")
def login_account_message(message):
    session = user_sessions.get(message.chat.id, {})
    if not session.get("In_ac", False):
        bot.send_message(message.chat.id, "Введите имя пользователя и пароль через запятую (например: Иван, 1234):")
        bot.register_next_step_handler(message, login_user)
    else:
        bot.send_message(message.chat.id, "Вы уже вошли в учётную запись.")

def login_user(message):
    try:
        # Парсим введённые данные
        name, password = map(str.strip, message.text.split(","))

        # Проверяем пользователя в базе данных
        user_data = requests.get(f"https://asmoraks.pythonanywhere.com/api/login/{name}/{password}")
        user_data = user_data.json()
        if user_data["status"] == "success":
            bot.send_message(message.chat.id, f"Добро пожаловать, {user_data['user_name']}! Ваши монеты: {user_data['user_coins']}.")
            user_sessions[message.chat.id] = {"In_ac": True, "user": user_data["user_name"] and user_data["user_id"]}
        else:
            bot.send_message(message.chat.id, "Ошибка: Неверное имя или пароль.")
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка! Убедитесь, что вы указали корректные данные через запятую.")

# Вывод списка лидеров
@bot.message_handler(func=lambda message: message.text == "Список лидеров")
def get_users_handler(message):
    user_data = requests.get("https://asmoraks.pythonanywhere.com/api/users/users_list").json()
    if user_data['status'] == 'success':
        user = user_data.get("users_list", [])
        bot.send_message(message.chat.id, user, parse_mode="MarkdownV2")
    else:
        bot.send_message(message.chat.id, "Список лидеров пуст.")

# Выход из аккаунта
@bot.message_handler(func=lambda message: message.text == "Выйти")
def log_out_account_message(message):
    session = user_sessions.get(message.chat.id, {})
    if session.get("In_ac", False):
        bot.send_message(message.chat.id, "Вы уверены, что хотите выйти из своей учетной записи?")
        bot.register_next_step_handler(message, log_out_account)
    else:
        bot.send_message(message.chat.id, "Вы не вошли в учётную запись.")

def log_out_account(message):
    if message.text == "да" or message.text == "Да":
        bot.send_message(message.chat.id, "Пока, пока.")
        user_sessions.pop(message.chat.id, None)
    elif message.text == "нет" or message.text == "Нет":
        bot.send_message(message.chat.id, "Ну вот и хорошо.")
    else:
       bot.send_message(message.chat.id, "Команда не распознана")

# Запуск бота
try:
    bot.infinity_polling()
except KeyboardInterrupt:
    print("Бот остановлен вручную.")
except Exception as e:
    print(f"Ошибка: {e}")