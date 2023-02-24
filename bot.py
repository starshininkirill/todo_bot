import telebot
from telebot import types
import sqlite3
from config import token
from utils import get_tasks_by_uid, add_task_to_db, delete_task_by_id, update_task_status, get_completed_tasks_by_uid


bot = telebot.TeleBot(token)

# cursor.execute("DROP TABLE test")
# cursor.execute("CREATE TABLE test(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, task VARCHAR(25), task_status INTEGER)")


@bot.message_handler(commands=['start'])
def start(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    btn_start = types.KeyboardButton(text="/start")
    btn_all = types.KeyboardButton(text="/all")
    btn_add = types.KeyboardButton(text="/add")
    btn_completed = types.KeyboardButton(text="/completed")
    kb.add(btn_start, btn_all, btn_add, btn_completed)
    bot.send_message(message.chat.id, """
        Привет, я бот, для составления списка дел, вот мои основные команды:\n
/start - Показать стартовое сообщение\n
/all - Показать весь список дел\n
/add - Добавить задачу\n
/completed - Показать выполненные задачи
        
    """, reply_markup=kb)


@bot.message_handler(commands=['all'])
def all(message):
    try:
        all_task = get_tasks_by_uid("test.db", message.from_user.id)
        if len(all_task) == 0:
            bot.send_message(message.chat.id, "Нет активных задач")
        else:
            bot.send_message(message.chat.id, "----------------")
            for task in all_task:
                kb = types.InlineKeyboardMarkup(row_width=1)
                btn_delete = types.InlineKeyboardButton(text="Удалить задачу", callback_data=f"delete_{task['task_id']}")
                btn_completed = types.InlineKeyboardButton(text="Выполненно", callback_data=f"completed_{task['task_id']}")
                kb.add(btn_delete, btn_completed)
                bot.send_message(message.chat.id, f"Задача: {task['task']}", reply_markup=kb)
            bot.send_message(message.chat.id, "----------------")
    except Exception:
        bot.send_message(message.chat.id, "Ошибка запроса к БД")


@bot.message_handler(commands=['completed'])
def completed(message):
    try:
        all_task = get_completed_tasks_by_uid("test.db", message.from_user.id)
        bot.send_message(message.chat.id, "----------------")
        for task in all_task:
            kb = types.InlineKeyboardMarkup(row_width=1)
            btn_delete = types.InlineKeyboardButton(text="Удалить задачу", callback_data=f"delete_{task['task_id']}")
            kb.add(btn_delete)
            bot.send_message(message.chat.id, f"Задача: {task['task']}", reply_markup=kb)
        bot.send_message(message.chat.id, "----------------")
    except Exception:
        bot.send_message(message.chat.id, "Ошибка запроса к БД")


@bot.message_handler(commands=['add'])
def add(message):
    sent = bot.reply_to(message, 'Напишите задачу, которую хотите добавить')
    bot.register_next_step_handler(sent, add_task)


def add_task(message):
    if add_task_to_db('test.db', message.from_user.id, message.text):
        bot.send_message(message.chat.id, f"Задача '{message.text}' успешно добавлена")
    else:
        bot.send_message(message.chat.id, "Ошибка добавления задачи")


@bot.callback_query_handler(func=lambda call: True)
def query_task(call):
    if call.message:
        if call.data[0] == "d":
            task_id = call.data.split("_")[-1]
            try:
                delete_task_by_id('test.db', task_id)
                bot.send_message(call.message.chat.id, f"Задача удалена")
                bot.delete_message(call.message.chat.id, call.message.id)
            except Exception:
                bot.send_message(call.message.chat.id, "Ошибка удаления задачи")
        elif call.data[0] == "c":
            task_id = call.data.split("_")[-1]
            try:
                update_task_status('test.db', task_id)
                bot.send_message(call.message.chat.id, "Задача выполнена")
                bot.delete_message(call.message.chat.id, call.message.id)
            except Exception:
                bot.send_message(call.message.chat.id, "Ошбика при выполнении запроса")
        bot.answer_callback_query(call.id)
    else:
        bot.answer_callback_query(call.id)


if __name__ == "__main__":
    bot.infinity_polling()
