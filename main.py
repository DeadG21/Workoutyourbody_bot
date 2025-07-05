import telebot
from telebot import types
import os
import logging
import sqlite3
from datetime import datetime, timedelta



# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен бота (лучше хранить в переменных окружения)
BOT_TOKEN = '7975399295:AAFE95_SzsFodq3j--HXgc2wE2fvXHoj3Jc'
bot = telebot.TeleBot(BOT_TOKEN)

def init_database():
    """Инициализация базы данных"""
    db_path = os.getenv('DATABASE_URL', 'fitness_bot.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            registration_date DATETIME,
            total_workouts INTEGER DEFAULT 0
        )
    ''')

    # Таблица выполненных тренировок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workout_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            workout_type TEXT,
            workout_name TEXT,
            completed_date DATETIME,
            exercises_count INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    conn.commit()
    conn.close()

init_database()

def add_user(user_id, username, first_name, last_name):
    """Добавление нового пользователя"""
    conn = sqlite3.connect('fitness_bot.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR IGNORE INTO users 
        (user_id, username, first_name, last_name, registration_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, last_name, datetime.now()))

    conn.commit()
    conn.close()


def save_workout(user_id, workout_type, workout_name, exercises_count):
    """Сохранение выполненной тренировки"""
    conn = sqlite3.connect('fitness_bot.db')
    cursor = conn.cursor()

    # Сохраняем тренировку
    cursor.execute('''
        INSERT INTO workout_history 
        (user_id, workout_type, workout_name, completed_date, exercises_count)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, workout_type, workout_name, datetime.now(), exercises_count))

    # Обновляем счетчик тренировок пользователя
    cursor.execute('''
        UPDATE users 
        SET total_workouts = total_workouts + 1 
        WHERE user_id = ?
    ''', (user_id,))

    conn.commit()
    conn.close()


def get_user_stats(user_id):
    """Получение статистики пользователя"""
    conn = sqlite3.connect('fitness_bot.db')
    cursor = conn.cursor()

    # Общая статистика
    cursor.execute('''
        SELECT total_workouts, registration_date 
        FROM users 
        WHERE user_id = ?
    ''', (user_id,))

    user_data = cursor.fetchone()

    if not user_data:
        conn.close()
        return None

    total_workouts, reg_date = user_data

    # Статистика за последнюю неделю
    week_ago = datetime.now() - timedelta(days=7)
    cursor.execute('''
        SELECT COUNT(*) FROM workout_history 
        WHERE user_id = ? AND completed_date >= ?
    ''', (user_id, week_ago))

    week_workouts = cursor.fetchone()[0]

    # Любимый тип тренировки
    cursor.execute('''
        SELECT workout_type, COUNT(*) as count
        FROM workout_history 
        WHERE user_id = ?
        GROUP BY workout_type
        ORDER BY count DESC
        LIMIT 1
    ''', (user_id,))

    favorite_result = cursor.fetchone()
    favorite_workout = favorite_result[0] if favorite_result else "Нет данных"

    conn.close()

    return {
        'total_workouts': total_workouts,
        'week_workouts': week_workouts,
        'favorite_workout': favorite_workout,
        'registration_date': reg_date
    }

# Структуры данных для тренировок
WORKOUTS = {
    'morning': {
        'name': 'Утренняя тренировка',
        'exercises': [
            {
                'name': 'Вращения головой полукругом',
                'file': None,
                'duration': '30 секунд',
                'description': '''
🔄 <b>ТЕХНИКА ВЫПОЛНЕНИЯ:</b>
1. Встаньте прямо, расслабьте плечи
2. Медленно поверните голову вправо до упора
3. Опустите подбородок к груди
4. Поверните голову влево до упора
5. Вернитесь в исходное положение

⚠️ <b>ВАЖНО:</b> НЕ запрокидывайте голову назад!
💡 <b>ЭФФЕКТ:</b> Улучшает кровообращение, снимает напряжение'''
            },
            {
                'name': 'Наклоны головы вперед-назад',
                'file': None,
                'duration': '20 секунд',
                'description': '''
↕️ <b>ТЕХНИКА ВЫПОЛНЕНИЯ:</b>
1. Встаньте прямо, взгляд вперед
2. Медленно опустите подбородок к груди
3. Почувствуйте растяжение задней поверхности шеи
4. Медленно поднимите голову вверх
5. Немного откиньте голову назад (осторожно!)

⚠️ <b>ВАЖНО:</b> Все движения плавные, без рывков
💡 <b>ЭФФЕКТ:</b> Растягивает мышцы шеи, убирает зажимы'''
            },
            {
                'name': 'Круговые движения плечами',
                'file': None,
                'duration': '30 секунд',
                'description': '''
🔄 <b>ТЕХНИКА ВЫПОЛНЕНИЯ:</b>
1. Встаньте прямо, руки вдоль тела
2. Поднимите плечи вверх к ушам
3. Отведите плечи назад
4. Опустите плечи вниз
5. Подайте плечи вперед

⚠️ <b>ВАЖНО:</b> Делайте 10 раз вперед, 10 раз назад
💡 <b>ЭФФЕКТ:</b> Разминает плечевые суставы, улучшает осанку'''
            },
            {
                'name': 'Наклоны туловища',
                'file': None,
                'duration': '30 секунд',
                'description': '''
↔️ <b>ТЕХНИКА ВЫПОЛНЕНИЯ:</b>
1. Встаньте прямо, ноги на ширине плеч
2. Поднимите одну руку вверх
3. Наклонитесь в противоположную сторону
4. Почувствуйте растяжение в боку
5. Вернитесь в центр и повторите в другую сторону

⚠️ <b>ВАЖНО:</b> Не наклоняйтесь вперед или назад
💡 <b>ЭФФЕКТ:</b> Растягивает косые мышцы живота'''
            }
        ]
    },
    'lunch': {
        'name': 'Обеденная тренировка',
        'exercises': [
            {
                'name': 'Отжимания от стола',
                'file': None,
                'duration': '10 раз',
                'description': '''
💪 <b>ТЕХНИКА ВЫПОЛНЕНИЯ:</b>
1. Встаньте в метре от стола
2. Упритесь ладонями в край стола
3. Тело держите прямо, как планка
4. Сгибайте руки, приближаясь к столу
5. Выпрямляйте руки, отталкиваясь от стола

⚠️ <b>ВАЖНО:</b> Не прогибайтесь в пояснице
💡 <b>ЭФФЕКТ:</b> Укрепляет грудные мышцы, трицепсы'''
            },
            {
                'name': 'Приседания',
                'file': None,
                'duration': '15 раз',
                'description': '''
🦵 <b>ТЕХНИКА ВЫПОЛНЕНИЯ:</b>
1. Встаньте прямо, ноги на ширине плеч
2. Руки вытяните вперед или на пояс
3. Медленно присядьте, отводя таз назад
4. Колени не должны выходить за носки
5. Поднимитесь, напрягая ягодицы

⚠️ <b>ВАЖНО:</b> Спина прямая, вес на пятках
💡 <b>ЭФФЕКТ:</b> Укрепляет ноги и ягодицы, улучшает кровообращение'''
            },
            {
                'name': 'Планка',
                'file': None,
                'duration': '30 секунд',
                'description': '''
🏋️‍♂️ <b>ТЕХНИКА ВЫПОЛНЕНИЯ:</b>
1. Лягте на живот
2. Поднимитесь на предплечья и носки
3. Тело должно быть прямой линией
4. Напрягите пресс и ягодицы
5. Дышите ровно, удерживайте позицию

⚠️ <b>ВАЖНО:</b> Не поднимайте таз вверх, не прогибайтесь
💡 <b>ЭФФЕКТ:</b> Укрепляет весь корпус, улучшает стабильность'''
            }
        ]
    },
    'evening': {
        'name': 'Вечерняя тренировка',
        'exercises': [
            {
                'name': 'Растяжка шеи',
                'file': None,
                'duration': '30 секунд',
                'description': '''
🧘‍♀️ <b>ТЕХНИКА ВЫПОЛНЕНИЯ:</b>
1. Сядьте удобно, спина прямая
2. Положите правую руку на левое ухо
3. Мягко потяните голову к правому плечу
4. Держите 15 секунд
5. Повторите в другую сторону

⚠️ <b>ВАЖНО:</b> Не применяйте силу, только легкое натяжение
💡 <b>ЭФФЕКТ:</b> Расслабляет шею после рабочего дня'''
            },
            {
                'name': 'Растяжка спины',
                'file': None,
                'duration': '30 секунд',
                'description': '''
🤸‍♂️ <b>ТЕХНИКА ВЫПОЛНЕНИЯ:</b>
1. Сядьте на пол, ноги вытянуты
2. Медленно наклонитесь вперед
3. Тянитесь руками к стопам
4. Почувствуйте растяжение в спине
5. Дышите глубоко и расслабьтесь

⚠️ <b>ВАЖНО:</b> Не делайте резких движений
💡 <b>ЭФФЕКТ:</b> Снимает напряжение с позвоночника'''
            },
            {
                'name': 'Дыхательные упражнения',
                'file': None,
                'duration': '1 минута',
                'description': '''
🫁 <b>ТЕХНИКА ВЫПОЛНЕНИЯ:</b>
1. Сядьте удобно, спина прямая
2. Положите одну руку на грудь, другую на живот
3. Вдохните носом на 4 счета (живот поднимается)
4. Задержите дыхание на 2 счета
5. Выдохните ртом на 6 счетов (живот опускается)

⚠️ <b>ВАЖНО:</b> Дышите животом, а не грудью
💡 <b>ЭФФЕКТ:</b> Успокаивает нервную систему, подготавливает ко сну'''
            }
        ]
    }
}

# Словарь для отслеживания состояния пользователей
user_states = {}


def get_main_keyboard():
    """Создает основную клавиатуру"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton('🌅 Утренняя тренировка'),
        types.KeyboardButton('🌞 Обеденная тренировка')
    )
    markup.add(
        types.KeyboardButton('🌙 Вечерняя тренировка'),
        types.KeyboardButton('💪 Свободная тренировка')
    )
    markup.add(
        types.KeyboardButton('📊 Статистика'),  # Новая кнопка
        types.KeyboardButton('ℹ️ Помощь')
    )
    return markup


def get_exercise_keyboard():
    """Создает клавиатуру для упражнений"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton('▶️ Далее'),
        types.KeyboardButton('⏸️ Пауза')
    )
    markup.add(
        types.KeyboardButton('🔄 Повторить'),
        types.KeyboardButton('🏠 В главное меню')
    )
    return markup


def get_free_workout_keyboard():
    """Создает клавиатуру для свободной тренировки"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton('🧠 Голова и шея'),
        types.KeyboardButton('💪 Руки и плечи')
    )
    markup.add(
        types.KeyboardButton('🫁 Грудь и спина'),
        types.KeyboardButton('🦵 Ноги')
    )
    markup.add(
        types.KeyboardButton('🏠 В главное меню')
    )
    return markup


@bot.message_handler(commands=['start'])
def start_command(message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""

    # Добавляем пользователя в базу
    add_user(user_id, username, first_name, last_name)

    user_states[user_id] = {'current_workout': None, 'current_exercise': 0}

    welcome_text = f"Привет, {first_name} {last_name}! 👋\n\n" \
                   f"Добро пожаловать в фитнес-бота! 💪\n" \
                   f"Если ты нажал кнопку старт, значит готов к совершенствованию.\n\n" \
                   f"Выбери тип тренировки из меню ниже:"

    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=get_main_keyboard()
    )


@bot.message_handler(commands=['help'])
def help_command(message):
    """Обработчик команды /help"""
    help_text = """
🤖 <b>Команды бота:</b>

/start - начать работу с ботом
/help - показать это сообщение
/reset - сбросить текущую тренировку

🏋️‍♂️ <b>Типы тренировок:</b>

🌅 <b>Утренняя</b> - легкая разминка для начала дня
🌞 <b>Обеденная</b> - короткая активность в обеденный перерыв  
🌙 <b>Вечерняя</b> - расслабляющие упражнения после работы
💪 <b>Свободная</b> - выбор упражнений по группам мышц

<b>Удачных тренировок!</b> 💪
    """
    bot.send_message(message.chat.id, help_text, parse_mode='HTML')


@bot.message_handler(commands=['reset'])
def reset_command(message):
    """Сброс текущей тренировки"""
    user_id = message.from_user.id
    if user_id in user_states:
        user_states[user_id] = {'current_workout': None, 'current_exercise': 0}

    bot.send_message(
        message.chat.id,
        "Тренировка сброшена! Выбери новую тренировку:",
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(commands=['stats'])
def stats_command(message):
    """Показать статистику пользователя"""
    user_id = message.from_user.id
    stats = get_user_stats(user_id)

    if not stats:
        bot.send_message(message.chat.id, "❌ Данные не найдены. Начните с команды /start")
        return

    # Преобразуем тип тренировки в читаемый вид
    workout_names = {
        'morning': '🌅 Утренняя',
        'lunch': '🌞 Обеденная',
        'evening': '🌙 Вечерняя'
    }

    favorite_name = workout_names.get(stats['favorite_workout'], stats['favorite_workout'])

    # Форматируем дату регистрации
    reg_date = datetime.fromisoformat(stats['registration_date']).strftime('%d.%m.%Y')

    stats_text = f"📊 <b>Твоя статистика</b>\n\n" \
                 f"🏋️‍♂️ <b>Всего тренировок:</b> {stats['total_workouts']}\n" \
                 f"📅 <b>За последнюю неделю:</b> {stats['week_workouts']}\n" \
                 f"❤️ <b>Любимая тренировка:</b> {favorite_name}\n" \
                 f"📈 <b>С нами с:</b> {reg_date}\n\n"

    # Добавляем мотивирующее сообщение
    if stats['total_workouts'] == 0:
        stats_text += "💪 Время начать! Выбери свою первую тренировку!"
    elif stats['total_workouts'] < 5:
        stats_text += "🔥 Отличное начало! Продолжай в том же духе!"
    elif stats['total_workouts'] < 20:
        stats_text += "⭐ Ты уже в хорошей форме! Не останавливайся!"
    else:
        stats_text += "🏆 Ты настоящий чемпион! Невероятная дисциплина!"

    bot.send_message(message.chat.id, stats_text, parse_mode='HTML')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Основной обработчик сообщений"""
    user_id = message.from_user.id
    text = message.text

    # Инициализация состояния пользователя если его нет
    if user_id not in user_states:
        user_states[user_id] = {'current_workout': None, 'current_exercise': 0}

    # Обработка главного меню
    if text in ['🌅 Утренняя тренировка', '🌞 Обеденная тренировка', '🌙 Вечерняя тренировка']:
        handle_workout_selection(message)
    elif text == '💪 Свободная тренировка':
        handle_free_workout(message)
    elif text == 'ℹ️ Помощь':
        help_command(message)
    elif text == '🏠 В главное меню':
        start_command(message)
    elif text in ['▶️ Далее', '⏸️ Пауза', '🔄 Повторить']:
        handle_exercise_control(message)
    elif text in ['🧠 Голова и шея', '💪 Руки и плечи', '🫁 Грудь и спина', '🦵 Ноги']:
        handle_body_part_selection(message)
    elif text == '📊 Статистика':
        stats_command(message)
    else:
        # Неизвестная команда
        bot.send_message(
            message.chat.id,
            "Не понимаю эту команду 🤔\nИспользуй кнопки меню или команду /help",
            reply_markup=get_main_keyboard()
        )


def handle_workout_selection(message):
    """Обработка выбора типа тренировки"""
    user_id = message.from_user.id
    text = message.text

    workout_map = {
        '🌅 Утренняя тренировка': 'morning',
        '🌞 Обеденная тренировка': 'lunch',
        '🌙 Вечерняя тренировка': 'evening'
    }

    workout_key = workout_map.get(text)
    if workout_key:
        user_states[user_id]['current_workout'] = workout_key
        user_states[user_id]['current_exercise'] = 0
        start_exercise(message, workout_key)


def start_exercise(message, workout_key):
    """Начинает упражнение"""
    user_id = message.from_user.id
    exercise_index = user_states[user_id]['current_exercise']
    workout = WORKOUTS[workout_key]

    if exercise_index < len(workout['exercises']):
        exercise = workout['exercises'][exercise_index]

        # Основная информация об упражнении
        exercise_text = f"🏋️‍♂️ <b>{workout['name']}</b>\n\n" \
                        f"<b>Упражнение {exercise_index + 1}/{len(workout['exercises'])}:</b>\n" \
                        f"🎯 {exercise['name']}\n\n" \
                        f"⏱️ <b>Длительность:</b> {exercise['duration']}\n\n"

        # Добавляем подробное описание
        if 'description' in exercise:
            exercise_text += exercise['description']

        bot.send_message(
            message.chat.id,
            exercise_text,
            parse_mode='HTML',
            reply_markup=get_exercise_keyboard()
        )

        # Отправка файла если есть
        if exercise['file'] and os.path.exists(exercise['file']):
            try:
                with open(exercise['file'], 'rb') as file:
                    bot.send_document(message.chat.id, file)
            except Exception as e:
                logging.error(f"Ошибка отправки файла: {e}")
                bot.send_message(message.chat.id, "❌ Не удалось загрузить файл с упражнением")
    else:
        # Тренировка завершена
        complete_workout(message)


def handle_exercise_control(message):
    """Обработка управления упражнениями"""
    user_id = message.from_user.id
    text = message.text
    state = user_states[user_id]

    if text == '▶️ Далее':
        if state['current_workout']:
            state['current_exercise'] += 1
            start_exercise(message, state['current_workout'])
        else:
            bot.send_message(message.chat.id, "Сначала выбери тренировку!")

    elif text == '⏸️ Пауза':
        bot.send_message(
            message.chat.id,
            "⏸️ Тренировка на паузе.\nОтдохни и продолжай когда будешь готов!",
            reply_markup=get_exercise_keyboard()
        )

    elif text == '🔄 Повторить':
        if state['current_workout']:
            start_exercise(message, state['current_workout'])


def complete_workout(message):
    """Завершение тренировки"""
    user_id = message.from_user.id
    workout_key = user_states[user_id]['current_workout']
    workout_name = WORKOUTS[workout_key]['name']
    exercises_count = len(WORKOUTS[workout_key]['exercises'])

    # Сохраняем тренировку в базу данных
    save_workout(user_id, workout_key, workout_name, exercises_count)

    completion_text = f"🎉 <b>Поздравляю!</b>\n\n" \
                      f"Ты успешно завершил: <b>{workout_name}</b>\n\n" \
                      f"💪 Отличная работа! Продолжай в том же духе!\n\n" \
                      f"Выбери следующую тренировку или отдохни:"

    # Сброс состояния
    user_states[user_id] = {'current_workout': None, 'current_exercise': 0}

    bot.send_message(
        message.chat.id,
        completion_text,
        parse_mode='HTML',
        reply_markup=get_main_keyboard()
    )


def handle_free_workout(message):
    """Обработка свободной тренировки"""
    bot.send_message(
        message.chat.id,
        "💪 <b>Свободная тренировка</b>\n\nВыбери группу мышц для тренировки:",
        parse_mode='HTML',
        reply_markup=get_free_workout_keyboard()
    )


def handle_body_part_selection(message):
    """Обработка выбора части тела для тренировки"""
    text = message.text

    exercises_map = {
        '🧠 Голова и шея': [
            "Повороты головы влево-вправо (10 раз)",
            "Наклоны головы вперед-назад (10 раз)",
            "Круговые движения головой (5 раз в каждую сторону)"
        ],
        '💪 Руки и плечи': [
            "Круговые движения плечами (10 раз)",
            "Отжимания от стены (10 раз)",
            "Подъемы рук вверх (15 раз)"
        ],
        '🫁 Грудь и спина': [
            "Сведение лопаток (10 раз)",
            "Наклоны туловища (10 раз)",
            "Прогибы спины (8 раз)"
        ],
        '🦵 Ноги': [
            "Приседания (15 раз)",
            "Подъемы на носки (20 раз)",
            "Выпады (10 раз каждой ногой)"
        ]
    }

    if text in exercises_map:
        exercises = exercises_map[text]
        exercise_text = f"<b>{text}</b>\n\n"
        for i, exercise in enumerate(exercises, 1):
            exercise_text += f"{i}. {exercise}\n"

        exercise_text += "\n💡 Выполняй упражнения в указанном порядке с отдыхом 30 секунд между упражнениями."

        bot.send_message(
            message.chat.id,
            exercise_text,
            parse_mode='HTML',
            reply_markup=get_free_workout_keyboard()
        )


if __name__ == "__main__":
    print("🤖 Бот запущен!")
    try:
        bot.infinity_polling(allowed_updates=['message'])
    except Exception as e:
        logging.error(f"Ошибка бота: {e}")
        print(f"❌ Ошибка: {e}")


