import logging
from telegram import Update, LabeledPrice
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    PreCheckoutQueryHandler
)
from telegram import ReplyKeyboardMarkup
import datetime
import asyncio
import psycopg2
import re
import geopy
import pytz
from tzwhere import tzwhere
import uuid

dbname = "postgres"
user = "vsevolod12"
password = "Vm205912"
host = "localhost" 
port = "5432" 


connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

MIDLE_OPTION, CHOOSE_OPTION, REGISTRATION_INFO, REMINDER, ADD_TASK, ROLE, CITY, COMENTS, LIKES, REPOSTS, CHOOSE_TYPE, GET_TASK = range(1, 12)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = connection.cursor()
    create_table_query = '''CREATE TABLE IF NOT EXISTS registr
                         (id SERIAL PRIMARY KEY,
                          linkedURL VARCHAR(100),
                          city VARCHAR(50),
                          time_zone VARCHAR(10),
                          role VARCHAR(200),
                          status INTEGER DEFAULT 0,
                          engage_rate INTEGER DEFAULT 1);'''
    cursor.execute(create_table_query)
    connection.commit()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Приветсвтвие и правила пользования",
        
    )
    cursor.execute("INSERT INTO registr (id) VALUES (%s) ON CONFLICT (id) DO NOTHING", (update.effective_user.id,))
    connection.commit()
    return await midle_option(update, context)



async def midle_option(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Напишите пожалуйста вашу ссылку на linkedin"
        )
    return REGISTRATION_INFO

async def reg_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = connection.cursor()
    pattern = r'^https?://(www\.)?linkedin\.com/.*$'
    url = update.effective_message.text
    if re.match(pattern, url):
        insert_query = '''UPDATE registr SET linkedURL = %s WHERE id = %s;'''
        new_user = (url)
        cursor.execute(insert_query, (new_user, update.effective_user.id,))
        connection.commit()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="напишите вашу роль"
            )
        return ROLE
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Не правильная ссылка"
        )
        return await midle_option(update, context)
async def city(update: Update, context:ContextTypes.DEFAULT_TYPE):
    cursor = connection.cursor()
    city = update.effective_message.text
    insert_query = '''UPDATE registr SET city = %s WHERE id = %s;'''
    new_user = (city)
    cursor.execute(insert_query, (new_user, update.effective_user.id,))
    connection.commit()
    return await time_zone(update, context)
async def role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = connection.cursor()
    role = update.effective_message.text
    insert_query = '''UPDATE registr SET role = %s WHERE id = %s;'''
    new_user = (role)
    cursor.execute(insert_query, (new_user, update.effective_user.id,))
    connection.commit()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="введите ваш город"
    )
    return CITY
    
async def time_zone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = connection.cursor()
    select_query = '''SELECT city FROM registr WHERE id = %s;'''
    cursor.execute(select_query, (update.effective_user.id,))
    city = cursor.fetchone()
    geo = geopy.geocoders.Nominatim(user_agent="SuperMon_Bot")
    location = geo.geocode(city)
    if location is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Не могу найти ваш временной пояс по данному городу, попробуйте другой город или напишите правильно"
        )
        return CITY
    else:
        tzw = tzwhere.tzwhere() 
        timezone_str = tzw.tzNameAt(location.latitude,location.longitude) # получаем название часового пояса
        tz = pytz.timezone(timezone_str)
        tz_info = datetime.datetime.now(tz=tz).strftime("%z") # получаем смещение часового пояса
        tz_info = tz_info[0:3]+":"+tz_info[3:] # приводим к формату ±ЧЧ:ММ
        insert_query = '''UPDATE registr SET time_zone WHERE id = %s;'''
        new_user = (timezone_str)
        cursor.execute(insert_query, (new_user, update.effective_user.id,))
        connection.commit()
        return await menu(update, context)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Добавить задачу","Решать задачи"]]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите опцию",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    return CHOOSE_OPTION

async def choose_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = connection.cursor()
    if update.effective_message.id == "Добавить задачу":
        cursor.execute('''SELECT status FROM registr WHERE id = %s;''', (update.effective_user.id,))
        status = cursor.fetchone()[0]
        status = int(status)
        if status == 5:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="На сегодня вы больше не моежете создавать задачи, это возможность вновь разблокируется через 24 часа"
            )

            return await menu(update, context)
        else:
            return write_function(update, context)
    
async def write_function(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Напишите вашу ссылку на linkein"
    )
    return ADD_TASK
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Лайки","Комент","Репост"]]
    cursor = connection.cursor()
    create_table_query = '''CREATE TABLE IF NOT EXISTS add_task
                         (task_id SERIAL PRIMARY KEY,
                          task_type VARCHAR(100),
                          linked_url VARCHAR(300),
                          many INTEGER,
                          much INTEGER,
                          user_id INTEGER REFERENCES registr(id));'''
    cursor.execute(create_table_query)
    connection.commit()
    pattern = r'^https?://(www\.)?linkedin\.com/.*$'
    url = update.effective_message.text
    if re.match(pattern, url):
        task_id = str(uuid.uuid4())
        context.user_data["task_id"] = task_id
        insert_task_id = '''UPDATE add_task SET task_id = %s WHERE user_id = %s;'''
        new_task_id = (task_id)
        cursor.execute(insert_task_id, (new_task_id, update.effective_user.id,))
        connection.commit()
        insert_query = '''UPDATE add_task SET linked_url = %s WHERE task_id = %s;'''
        new_task = (url)
        cursor.execute(insert_query, (new_task, task_id,))
        connection.commit()
        cursor.execute('''SELECT status FROM registr WHERE id = %s;''', (update.effective_user.id,))
        status = cursor.fetchone()[0]
        status = int(status)
        status += 1
        insert_query2 = '''UPDATE registr SET status = %s WHERE user_id = %s;'''
        new_task2 = (status)
        cursor.execute(insert_query2, (new_task2, update.effective_user.id,))
        connection.commit()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="выберите вид вашей задачи",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        return CHOOSE_TYPE
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Не правильная ссылка"
        )
        return await write_function(update, context)
async def choose_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = connection.cursor()
    task_id = context.user_data["task_id"]
    if update.effective_message.text == "Лайки":
        insert_query1 = '''UPDATE add_task SET task_type = %s WHERE task_id = %s;'''
        new_task = ("like")
        cursor.execute(insert_query1, (new_task, task_id))
        connection.commit()
        return await many_likes_text(update, context)
    if update.effective_message.text == "Комент":
        insert_query2 = '''UPDATE add_task SET task_type = %s WHERE task_id = %s;'''
        new_task_2 = ("coment")
        cursor.execute(insert_query2, (new_task_2, task_id))
        connection.commit()
        return await many_coments_text(update, context)
    if update.effective_message.text == "Репост":
        insert_query3 = '''UPDATE add_task SET task_type = %s WHERE task_id = %s;'''
        new_task_3 = ("repost")
        cursor.execute(insert_query3, (new_task_3, task_id))
        connection.commit()
        return await many_reposts_text(update, context)
        
async def many_likes_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Напишите желаемое количество лайков"
    )
    return LIKES
async def many_coments_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="напишите желаемое количество коментов"
    )
    return COMENTS
async def many_reposts_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="ввидите жедаемое количество репостов"
    )
    return REPOSTS
async def many_likes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyback = [["Добавить задачу","Решать задачи"]]
    cursor = connection.cursor()
    likes = int(update.effective_message.text)
    task_id = context.user_data["task_id"]
    if likes <= 5 and likes > 0:
        insert_query = '''UPDATE add_task SET many = %s WHERE task_id = %s;'''
        new_task = (likes)
        cursor.execute(insert_query, (new_task, task_id))
        connection.commit()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Что хотите делать дальше",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyback, 
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        return CHOOSE_OPTION
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Количество лайков не может быть больше пяти в одном задании"
        )
        return await many_likes_text(update, context)
async def many_coments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyback = [["Добавить задачу","Решать задачи"]]
    cursor = connection.cursor()
    coments = int(update.effective_mesage.text)
    task_id = context.user_data["task_id"]
    if coments <= 3 and coments > 0:
        insert_query = '''UPDATE add_task SET many = %s WHERE task_id = %s;'''
        new_task = (coments)
        cursor.execute(insert_query, (new_task, task_id))
        connection.commit()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Что хотите делать дальше",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyback, 
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        return CHOOSE_OPTION
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Количество кометов не может привышать три в одном задании"
        )
        return await many_coments_text(update, context)
async def many_reposts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyback = [["Добавить задачу","Решать задачи"]]
    cursor = connection.cursor()
    reposts = int(update.effective_message.text)
    task_id = context.user_data["task_id"]
    if reposts == 1:
        insert_query = '''UPDATE add_task SET many = %s WHERE task_id = %s;'''
        new_task = (reposts)
        cursor.execute(insert_query, (new_task, task_id))
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Что хотите делать дальше",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyback, 
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        return CHOOSE_OPTION
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            tetx="количество репотво не модет привышать один за одно задание"
        )
        return await many_reposts_text(update, context)


    
