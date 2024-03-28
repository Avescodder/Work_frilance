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

MIDLE_OPTION, CHOOSE_OPTION, REGISTRATION_INFO = range(1, 3)

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
            insert_query = '''INSERT INTO registr (linkedURL) VALUES (%s);'''
            new_user = (url)
            cursor.execute(insert_query, new_user)
            connection.commit()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="введите ваш город"
            )
            return await city(update, context)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Не праивльная ссылка"
            )
            return midle_option(update, context)
    async def city(update: Update, context:ContextTypes.DEFAULT_TYPE):
        city = update.effective_message.text
        insert_query = '''INSERT INTO registr (city) VALUES (%s);'''
        new_user = (city)
        cursor.execute(insert_query, new_user)
        connection.commit()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="напишите вашу роль"
        )
        return await role(update, context)
    async def role(update: Update, context: ContextTypes.DEFAULT_TYPE):
        role = update.effective_message.text
        insert_query = '''INSERT INTO registr (role) VALUES (%s)'''
        new_user = (role)
        cursor.execute(insert_query, new_user)
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


