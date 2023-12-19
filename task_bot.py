import telebot
from telebot import types

bot = telebot.TeleBot('')
tasks = {}  # Dictionary to store tasks for each user

@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    test_button = types.KeyboardButton('Тест')
    add_task_button = types.KeyboardButton('Добавить задачу')
    show_tasks_button = types.KeyboardButton('Показать все задачи')
    delete_task_button = types.KeyboardButton('Удалить запись')
    delete_all_button = types.KeyboardButton('Удалить все записи')
    markup.add(test_button, add_task_button, show_tasks_button, delete_task_button, delete_all_button)

    bot.send_message(message.chat.id, "Привет! Я твой тестовый бот. Нажми 'Тест' для приветствия, 'Добавить задачу' для добавления новой задачи, 'Показать все задачи' для просмотра задач, 'Удалить запись' для удаления задач, 'Удалить все записи' для удаления всех задач.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Тест')
def handle_test(message):
    bot.send_message(message.chat.id, "Привет! Я твой бот. Как дела?")

@bot.message_handler(func=lambda message: message.text == 'Добавить задачу')
def handle_add_task(message):
    bot.send_message(message.chat.id, "Введи название задачи:")
    bot.register_next_step_handler(message, add_task)

def add_task(message):
    task_name = message.text
    user_id = message.from_user.id

    if user_id not in tasks:
        tasks[user_id] = []

    task_number = len(tasks[user_id]) + 1
    tasks[user_id].append(f'{task_number}. {task_name}')
    bot.send_message(message.chat.id, f'Задача "{task_name}" добавлена успешно.')

@bot.message_handler(func=lambda message: message.text == 'Показать все задачи')
def handle_show_tasks(message):
    user_id = message.from_user.id

    if user_id in tasks and tasks[user_id]:
        task_list = '\n'.join(tasks[user_id])
        bot.send_message(message.chat.id, f'Твои задачи:\n{task_list}')
    else:
        bot.send_message(message.chat.id, 'У тебя нет задач.')

@bot.message_handler(func=lambda message: message.text == 'Удалить запись')
def handle_delete_task(message):
    bot.send_message(message.chat.id, "Выбери какую запись ты хочешь удалить (введи номер или полное название):")
    bot.register_next_step_handler(message, delete_task)

def delete_task(message):
    user_id = message.from_user.id
    choice = message.text.strip()

    if user_id in tasks and tasks[user_id]:
        task_deleted = False

        # Check if the choice is a number
        if choice.isdigit():
            task_number = int(choice)
            if 1 <= task_number <= len(tasks[user_id]):
                del tasks[user_id][task_number - 1]
                task_deleted = True

        # Check if the choice matches a task name
        elif any(choice in task for task in tasks[user_id]):
            tasks[user_id] = [task for task in tasks[user_id] if choice not in task]
            task_deleted = True

        if task_deleted:
            bot.send_message(message.chat.id, f'Запись успешно удалена.')
        else:
            bot.send_message(message.chat.id, f'Запись с номером или названием "{choice}" не найдена.')
    else:
        bot.send_message(message.chat.id, 'У тебя нет задач.')

@bot.message_handler(func=lambda message: message.text == 'Удалить все записи')
def handle_delete_all(message):
    user_id = message.from_user.id

    if user_id in tasks:
        del tasks[user_id]  # Remove all tasks for the user

    bot.send_message(message.chat.id, 'Все записи успешно удалены.')

# Обработка выхода из бота вручную (если бот прерван)
try:
    bot.polling(none_stop=True, interval=0)
except KeyboardInterrupt:
    pass
