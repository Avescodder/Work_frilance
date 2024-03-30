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

MIDLE_OPTION, CHOOSE_OPTION, REGISTRATION_INFO, REMINDER = range(1, 5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = connection.cursor()
    create_table_query = '''CREATE TABLE IF NOT EXISTS registr
                         (id SERIAL PRIMARY KEY,
                          linkedURL VARCHAR(100),
                          city VARCHAR(50),
                          time_zone VARCHAR(10),
                          role VARCHAR(200),
                          engage_rate INT(10)); '''
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
    reply_keyboard = [["Добавить задачу","Выполнить задачу"]]
    cursor = connection.cursor()
    pattern = r'^https?://(www\.)?linkedin\.com/.*$'
    async def linkedin(update: Update, context:ContextTypes.DEFAULT_TYPE):
        url = update.effective_message.text
        if re.match(pattern, url):
            insert_query = '''UPDATE registr SET linkedURL = %s WHERE id = %s;'''
            new_user = (url)
            cursor.execute(insert_query, (new_user, update.effective_user.id))
            connection.commit()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="напишите вашу роль"
            )
            return await role(update, context)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Не правильная ссылка"
            )
            return midle_option(update, context)
    async def city(update: Update, context:ContextTypes.DEFAULT_TYPE):
        city = update.effective_message.text
        insert_query = '''UPDATE registr SET city = %s WHERE id = %s;'''
        new_user = (city)
        cursor.execute(insert_query, (new_user, update.effective_user.id))
        connection.commit()
        return await time_zone(update, context)
    async def role(update: Update, context: ContextTypes.DEFAULT_TYPE):
        role = update.effective_message.text
        insert_query = '''UPDATE registr SET role = %s WHERE id = %s;'''
        new_user = (role)
        cursor.execute(insert_query, (new_user, update.effective_user.id))
        connection.commit()
        return await rating(update, context)
    async def rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
        rating = 1
        insert_query = '''UPDATE registr SET engage_rate = %s WHERE id = %s;'''
        new_user = (rating)
        cursor.execute(insert_query, (new_user, update.effective_user.id))
        connection.commit()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="введите ваш город"
        )
        return await city(update, context)
    
    async def time_zone(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            return await city(update, context)
        else:
            tzw = tzwhere.tzwhere() 
            timezone_str = tzw.tzNameAt(location.latitude,location.longitude) # получаем название часового пояса
            tz = pytz.timezone(timezone_str)
            tz_info = datetime.datetime.now(tz=tz).strftime("%z") # получаем смещение часового пояса
            tz_info = tz_info[0:3]+":"+tz_info[3:] # приводим к формату ±ЧЧ:ММ
            insert_query = '''UPDATE registr SET time_zone WHERE id = %s;'''
            new_user = (timezone_str)
            cursor.execute(insert_query, (new_user, update.effective_user.id))
            connection.commit()
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
    return await linkedin(update, context)