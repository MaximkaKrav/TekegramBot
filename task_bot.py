import telebot
from telebot import types

# Чтение токена из файла
with open('token.txt', 'r') as file:
    TOKEN = file.read().strip()

bot = telebot.TeleBot(TOKEN)

tasks = {}  # Dictionary to store tasks for each user
user_states = {}  # Dictionary to track user states

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    if user_id not in user_states:
        user_states[user_id] = {'first_start': True}
        send_welcome_message(message)
    else:
        update_keyboard(message)

def send_welcome_message(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    add_task_button = types.KeyboardButton('Добавить задачу')
    show_tasks_button = types.KeyboardButton('Показать все задачи')
    markup.add(add_task_button, show_tasks_button)

    bot.send_message(message.chat.id, "👋 Привет! Я твой менеджер задач. Что будем делать?", reply_markup=markup)
    user_states[message.from_user.id]['first_start'] = False

def update_keyboard(message):
    user_id = message.from_user.id
    markup = types.ReplyKeyboardMarkup(row_width=2)
    add_task_button = types.KeyboardButton('Добавить задачу')
    show_tasks_button = types.KeyboardButton('Показать все задачи')

    # Проверяем наличие задач для данного пользователя
    if user_id in tasks and tasks[user_id]:
        delete_task_button = types.KeyboardButton('Удалить запись')
        delete_all_button = types.KeyboardButton('Удалить все записи')
        markup.add(add_task_button, show_tasks_button, delete_task_button, delete_all_button)
    else:
        markup.add(add_task_button, show_tasks_button)

    bot.send_message(message.chat.id, "Что дальше?", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Добавить задачу')
def handle_add_task(message):
    bot.send_message(message.chat.id, "📝 Введи название задачи:")
    bot.register_next_step_handler(message, add_task)


def add_task(message):
    task_name = message.text
    user_id = message.from_user.id

    if user_id not in tasks:
        tasks[user_id] = []

    task_number = len(tasks[user_id]) + 1
    tasks[user_id].append(f'✅ {task_number}. {task_name}')
    bot.send_message(message.chat.id, f'👍 Задача "{task_name}" добавлена успешно.')

    # Обновление клавиатуры после добавления задачи
    update_keyboard(message)


@bot.message_handler(func=lambda message: message.text == 'Показать все задачи')
def handle_show_tasks(message):
    user_id = message.from_user.id

    if user_id in tasks and tasks[user_id]:
        task_list = '\n'.join(tasks[user_id])
        bot.send_message(message.chat.id, f'📋 Твои задачи:\n{task_list}')
    else:
        bot.send_message(message.chat.id, '🤔 У тебя нет задач.')

    # Обновление клавиатуры после просмотра задач
    update_keyboard(message)


@bot.message_handler(func=lambda message: message.text == 'Удалить запись')
def handle_delete_task(message):
    bot.send_message(message.chat.id, "🗑️ Выбери какую запись ты хочешь удалить (введи номер или полное название):")
    bot.register_next_step_handler(message, delete_task)


def delete_task(message):
    user_id = message.from_user.id
    choice = message.text.strip()

    if user_id in tasks and tasks[user_id]:
        task_deleted = False

        # Проверяем, существуют ли задачи
        if choice.isdigit() and 1 <= int(choice) <= len(tasks[user_id]):
            # Если выбран номер задачи
            del tasks[user_id][int(choice) - 1]
            task_deleted = True
        elif any(choice in task for task in tasks[user_id]):
            # Если выбрано полное название задачи
            tasks[user_id] = [task for task in tasks[user_id] if choice not in task]
            task_deleted = True

        if task_deleted:
            bot.send_message(message.chat.id, f'🗑️ Запись успешно удалена.')
        else:
            bot.send_message(message.chat.id, f'❌ Запись с номером или названием "{choice}" не найдена.')
    else:
        bot.send_message(message.chat.id, '🤔 У тебя нет задач.')

    # Обновление клавиатуры после удаления задачи
    update_keyboard(message)


@bot.message_handler(func=lambda message: message.text == 'Удалить все записи')
def handle_delete_all(message):
    user_id = message.from_user.id

    if user_id in tasks:
        del tasks[user_id]  # Удаляем все задачи пользователя

    bot.send_message(message.chat.id, '🗑️ Все записи успешно удалены.')

    # Обновление клавиатуры после удаления всех задач
    update_keyboard(message)


# Обработка выхода из бота вручную (если бот прерван)
try:
    bot.polling(none_stop=True, interval=0)
except KeyboardInterrupt:
    pass
