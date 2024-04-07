import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler
)
from telegram import ReplyKeyboardMarkup
import datetime
import psycopg2
import re
import pytz
import uuid
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import schedule

dbname = "first_bot"
user = "postgres"
password = "Vm205912"
host = "localhost" 
port = "5432" 


try:
    connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cursor = connection.cursor()
    print("Подключение к базе данных успешно!")


except (Exception, psycopg2.Error) as error:
    print("Ошибка при подключении к базе данных PostgreSQL:", error)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

(CHOOSE_OPTION, REGISTRATION_INFO, ADD_TASK, ROLE, CITY, COMENTS, LIKES, REPOSTS, CHOOSE_TYPE, SKILLS, FOLLOWS, ERROR) = range(12)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = connection.cursor()
    create_table_query = '''CREATE TABLE IF NOT EXISTS registr
                         (id SERIAL PRIMARY KEY,
                          linkedURL VARCHAR(500),
                          city VARCHAR(50),
                          time_zone VARCHAR(100),
                          role VARCHAR(200),
                          status INTEGER DEFAULT 0,
                          engage_rate INTEGER DEFAULT 1);'''
    cursor.execute(create_table_query)
    connection.commit()
    cursor.execute("INSERT INTO registr (id) VALUES (%s) ON CONFLICT (id) DO NOTHING", (update.effective_user.id,))
    connection.commit()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="""
Приветствуем вас в нашем боте,
тут будут правила и другая полезная информация. 
Чтобы начать пользоваться ботом нужно зарегистрироваться,
для этого вам потребуется ваша ссылка linkedin,
 потом просто выполняйте все по инструкциям бота.""",
        
    )
    return await midle_option(update, context)
    


async def midle_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = connection.cursor()
    user_id = update.effective_user.id
    select_query = '''SELECT linkedURL FROM registr WHERE id = %s;'''
    cursor.execute(select_query, (user_id,))
    rows = cursor.fetchall()
    print(rows)
    if rows and rows[0][0] is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Напишите пожалуйста вашу ссылку на Linkedin"
            )
        return REGISTRATION_INFO
    else:
        return await menu(update, context)
        # cursor.execute("UPDATE registr SET engage_rate = %s WHERE id = %s", (0, update.effective_user.id,))
        # connection.commit()
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
            text="""Напишите пожалуйста вашу роль, тут нужно будет написать объяснение что за роль, даже честно говоря не очень понял."""
            )
        return ROLE
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Вы ввели не корректную ссылку, проверьте ссылку и попробуйте еще раз."
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
        text="Введите пожалуйста ваш город, по нему мы определим ваш часовой пояс, для удобства пользования ботом."
    )
    return CITY
    
async def time_zone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = connection.cursor()
    select_query = '''SELECT city FROM registr WHERE id = %s;'''
    cursor.execute(select_query, (update.effective_user.id,))
    city = cursor.fetchone()[0]
    print(city)
    geo = Nominatim(user_agent="SuperMon_Bot")
    location = geo.geocode(city, language = 'ru')
    print(location)
    if location is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Не могу найти ваш временной пояс по данному городу, попробуйте другой, более крупный город, или напишите правильно"
        )
        return CITY
    else:
        lat, lon = location.latitude, location.longitude
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=lat, lng=lon)
        print(timezone_str)
        tz = pytz.timezone(timezone_str)
        tz_info = datetime.datetime.now(tz=tz).strftime("%z")
        tz_info = tz_info[0:3] + ":" + tz_info[3:] # приводим к формату ±ЧЧ:ММ
        print(tz_info)
        insert_query = '''UPDATE registr SET time_zone = %s WHERE id = %s;'''
        new_user = (timezone_str)
        cursor.execute(insert_query, (new_user, update.effective_user.id,))
        connection.commit()
        return await menu(update, context)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Добавить задачу","Решать задачи"]]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вы успешно зарегистрированы, теперь вы можете выполнять задания других пользователей или выставлять свои.",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    return CHOOSE_OPTION

async def choose_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = connection.cursor()
    if update.effective_message.text == "Добавить задачу":
        cursor.execute('''SELECT status FROM registr WHERE id = %s;''', (update.effective_user.id,))
        status = cursor.fetchone()[0]
        status = int(status)
        if status == 5:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="На сегодня вы больше не можете создавать задачи, это возможность вновь разблокируется через 24 часа"
            )

            return await menu(update, context)
        else:
            return await write_function(update, context)
    elif update.effective_message.text == "Решать задачи":
        return await send_top5(update, context)
    elif update.effective_message.text == "Да, конечно":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Отлично, можете приступать к выполнению задания!"
        )
        return await finishing_task(update, context)
    elif update.effective_message.text == "Нет, вернуться в меню":
        return await pull_back(update, context)
    elif update.effective_message.text == "Задание выполнено":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Отлично, вы выполнили задания, теперь вы вернётесь в главное меню. "
        )
        cursor.execute('''UPDATE do_task SET do_status = %s WHERE task_user_id = %s;''', ("1", update.effective_user.id,))
        connection.commit()
        return await menu(update, context)
async def write_function(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Напишите пожалуйста вашу ссылку на задание в LinkedIn."
    
    )
    return ADD_TASK
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Поставить лайки","Подписаться","Сделать репост"],["Написать комментарии","Одобрение навыка"]]
    cursor = connection.cursor()
    create_table_query = '''CREATE TABLE IF NOT EXISTS add_task
                         (task_id UUID PRIMARY KEY,
                          task_type VARCHAR(100),
                          linked_url VARCHAR(500),
                          many INTEGER,
                          much INTEGER,
                          rating INTEGER,
                          rate_calc_f INTEGER,
                          rate_calc_s INTEGER,
                          user_id INTEGER,
                          CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES registr(id));'''
    cursor.execute(create_table_query)
    connection.commit()
    pattern = r'^https?://(www\.)?linkedin\.com/.*$'
    url = update.effective_message.text
    cursor = connection.cursor()
    cursor.execute("UPDATE add_task SET rating = r.engage_rate FROM registr r INNER JOIN add_task t ON r.id = t.user_id;")
    connection.commit()

    if re.match(pattern, url):
        task_id = str(uuid.uuid4())
        context.user_data["task_id"] = task_id
        insert_query = '''INSERT INTO add_task (task_id, user_id) VALUES (%s, %s);'''
        cursor.execute(insert_query, (task_id, update.effective_user.id))
        connection.commit()
        insert_query = '''UPDATE add_task SET linked_url = %s WHERE task_id = %s;'''
        new_task = (url)
        cursor.execute(insert_query, (new_task, task_id,))
        connection.commit()
        cursor.execute('''SELECT status FROM registr WHERE id = %s;''', (update.effective_user.id,))
        status = cursor.fetchone()[0]
        status = int(status)
        status += 1
        insert_query2 = '''UPDATE registr SET status = %s WHERE id = %s;'''
        new_task2 = (status)
        cursor.execute(insert_query2, (new_task2, update.effective_user.id,))
        connection.commit()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Пожалуйста выберите тип вашей задачи",
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
    if update.effective_message.text == "Подписаться":
        insert_query0 = '''UPDATE add_task SET task_type = %s WHERE task_id = %s;'''
        new_task0 = ("Follow")
        cursor.execute(insert_query0, (new_task0, task_id))
        connection.commit()
        return await many_follows_text(update, context)
    elif update.effective_message.text == "Одобрение навыка":
        insert_query5 = '''UPDATE add_task SET task_type = %s WHERE task_id = %s;'''
        new = ("endorse_skill")
        cursor.execute(insert_query5, (new, task_id))
        connection.commit()
        return await many_skills_text(update, context)
    elif update.effective_message.text == "Поставить лайки":
        insert_query1 = '''UPDATE add_task SET task_type = %s WHERE task_id = %s;'''
        new_task = ("like")
        cursor.execute(insert_query1, (new_task, task_id))
        connection.commit()
        return await many_likes_text(update, context)
    elif update.effective_message.text == "Написать комментарии":
        insert_query2 = '''UPDATE add_task SET task_type = %s WHERE task_id = %s;'''
        new_task_2 = ("coment")
        cursor.execute(insert_query2, (new_task_2, task_id))
        connection.commit()
        return await many_coments_text(update, context)
    elif update.effective_message.text == "Сделать репост":
        insert_query3 = '''UPDATE add_task SET task_type = %s WHERE task_id = %s;'''
        new_task_3 = ("repost")
        cursor.execute(insert_query3, (new_task_3, task_id))
        connection.commit()
        return await many_reposts_text(update, context)
        
async def many_likes_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Напишите пожалуйста сколько лайков необходимо поставить."
    )
    return LIKES
async def many_coments_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Напишите пожалуйста сколько комментариев нужно написать."
    )
    return COMENTS
async def many_reposts_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Напишите пожалуйста сколько репостов нужно сделать."
    )
    return REPOSTS
async def many_follows_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Напишите пожалуйста сколько подписчиков хотите получить."
    )
    return FOLLOWS
async def many_skills_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Напишите пожалуйста сколько одобрений хотите получить."
    )
    return SKILLS
async def many_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyback = [["Добавить задачу","Решать задачи"]]
    cursor = connection.cursor()
    endorse = int(update.effective_message.text)
    task_id = context.user_data["task_id"]
    if endorse == 1:
        insert_query = '''UPDATE add_task SET many = %s WHERE task_id = %s;'''
        new_task = (endorse)
        cursor.execute(insert_query, (new_task, task_id))
        connection.commit()
        insert_query2 = '''UPDATE add_task SET rate_calc_f = %s WHERE task_id = %s;'''
        new_rate = 160
        new_rate = (new_rate)
        cursor.execute(insert_query2, (new_rate, task_id))
        connection.commit()
        insert_query3 = '''UPDATE add_task SET rate_calc_s = %s WHERE task_id = %s;'''
        new_rate2 = 1 / endorse
        new = (new_rate2)
        cursor.execute(insert_query3, (new, task_id))
        connection.commit()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Отлично, вы добавили задачу. Что предпочитаете делать далее?",
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
            text="Количество одобрений не может привышать одного на одно задание."
        )
        return await many_skills_text(update, context)
async def many_follows(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyback = [["Добавить задачу","Решать задачи"]]
    cursor = connection.cursor()
    follow = int(update.effective_message.text)
    task_id = context.user_data["task_id"]
    if follow <= 5 and follow > 0:
        insert_query = '''UPDATE add_task SET many = %s WHERE task_id = %s;'''
        new_task = (follow)
        cursor.execute(insert_query, (new_task, task_id))
        connection.commit()
        insert_query2 = '''UPDATE add_task SET rate_calc_f = %s WHERE task_id = %s;'''
        new_rate = 170
        new_rate = (new_rate)
        cursor.execute(insert_query2, (new_rate, task_id))
        connection.commit()
        insert_query3 = '''UPDATE add_task SET rate_calc_s = %s WHERE task_id = %s;'''
        new_rate2 = 5 / follow
        new = (new_rate2)
        cursor.execute(insert_query3, (new, task_id))
        connection.commit()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Отлично, вы добавили задачу. Что предпочитаете делать далее?",
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
            text="Количество подписок не может привышать пяти на одно задание."
        )
        return await many_follows_text(update, context)
async def many_likes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyback = [["Добавить задачу","Решать задачи"]]
    cursor = connection.cursor()
    likes = int(update.effective_message.text)
    task_id = context.user_data["task_id"]
    if likes <= 10 and likes > 0:
        insert_query = '''UPDATE add_task SET many = %s WHERE task_id = %s;'''
        new_task = (likes)
        cursor.execute(insert_query, (new_task, task_id))
        connection.commit()
        insert_query2 = '''UPDATE add_task SET rate_calc_f = %s WHERE task_id = %s;'''
        new_rate = 100
        new_rate = (new_rate)
        cursor.execute(insert_query2, (new_rate, task_id))
        connection.commit()
        insert_query3 = '''UPDATE add_task SET rate_calc_s = %s WHERE task_id = %s;'''
        new_rate2 = 10 / likes
        new = (new_rate2)
        cursor.execute(insert_query3, (new, task_id))
        connection.commit()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Отлично, вы добавили задачу. Что предпочитаете делать далее?",
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
            text="Количество лайков не может привышать десяти на одно задание."
        )
        return await many_likes_text(update, context)
async def many_coments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyback = [["Добавить задачу","Решать задачи"]]
    cursor = connection.cursor()
    coments = int(update.effective_message.text)
    task_id = context.user_data["task_id"]
    if coments <= 2 and coments > 0:
        insert_query = '''UPDATE add_task SET many = %s WHERE task_id = %s;'''
        new_task = (coments)
        cursor.execute(insert_query, (new_task, task_id))
        connection.commit()
        insert_query2 = '''UPDATE add_task SET rate_calc_f = %s WHERE task_id = %s;'''
        new_rate = 200
        new_rate = (new_rate)
        cursor.execute(insert_query2, (new_rate, task_id))
        connection.commit()
        insert_query3 = '''UPDATE add_task SET rate_calc_s = %s WHERE task_id = %s;'''
        new_rate2 = 2 / coments
        new = (new_rate2)
        cursor.execute(insert_query3, (new, task_id))
        connection.commit()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Отлично, вы создали задачу. Что предпочитаете делать далее?",
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
            text="Количество комментариев не может быть больше двух в одном заданиие."
        )
        return await many_coments_text(update, context)
async def many_reposts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyback = [["Добавить задачу","Решать задачи"]]
    cursor = connection.cursor()
    reposts = int(update.effective_message.text)
    task_id = context.user_data["task_id"]
    if reposts <= 3 or reposts > 0:
        insert_query = '''UPDATE add_task SET many = %s WHERE task_id = %s;'''
        new_task = (reposts)
        cursor.execute(insert_query, (new_task, task_id))
        connection.commit()
        insert_query2 = '''UPDATE add_task SET rate_calc_f = %s WHERE task_id = %s;'''
        new_rate = 130
        new_rate = (new_rate)
        cursor.execute(insert_query2, (new_rate, task_id))
        connection.commit()
        insert_query3 = '''UPDATE add_task SET rate_calc_s = %s WHERE task_id = %s;'''
        new_rate2 = 3 / reposts
        new = (new_rate2)
        cursor.execute(insert_query3, (new, task_id))
        connection.commit()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Отлично, вы создали задачу. Что предпочитаете делать далее?",
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
            text="Количество репостов не должно быть больше трёх на задание."
        )
        return await many_reposts_text(update, context)




async def send_top5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = connection.cursor()
    create_table_query = '''CREATE TABLE IF NOT EXISTS do_task
                         (do_task_id UUID PRIMARY KEY,
                          do_task_type VARCHAR(100),
                          do_linked_url VARCHAR(500),
                          do_many INTEGER,
                          task_user_id INTEGER,
                          do_rating INTEGER,
                          do_status INTEGER DEFAULT 0,
                          rate_calc_f INTEGER,
                          rate_calc_s INTEGER,
                          start_time TIMESTAMP,
                          first_user_id INTEGER,
                          CONSTRAINT fk_user_id FOREIGN KEY (task_user_id) REFERENCES registr(id));'''
    cursor.execute(create_table_query)
    connection.commit()
    reply_keyboard = [["Да, конечно","Нет, вернуться в меню"]]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Сейчас вы получите пять задач для выполнения, после выполнения ваш рейтинг вырастет"
    )
    cursor.execute('''
            SELECT task_id, task_type, linked_url, many, rating, user_id, rate_calc_f, rate_calc_s
            FROM add_task
            WHERE many > 0
            ORDER BY rating DESC
            LIMIT 5;
        ''')
    # Получаем результат запроса
    top_tasks = cursor.fetchall()
    print(top_tasks)

    
    total_rate = sum(rate[6] for rate in top_tasks)
    total_rate2 = sum(rate[7] for rate in top_tasks)
    revoke_coefficient = 1.1
    rank = (1 * total_rate * total_rate2) * revoke_coefficient
    print(rank)
    for task_id, task_type, linked_url, many, rating, user_id, rate_calc_f, rate_calc_s in top_tasks:
        insert = '''INSERT INTO do_task (do_task_id, task_user_id) VALUES (%s, %s);'''
        cursor.execute(insert, (task_id, update.effective_user.id))
        connection.commit()
        print(task_id)
        update_query = '''
        UPDATE do_task 
        SET do_task_type = %s,
            do_linked_url = %s,
            do_many = %s,
            do_rating = %s,
            rate_calc_f = %s,
            first_user_id = %s
        WHERE task_user_id = %s'''
        cursor.execute(update_query, (task_type, linked_url, many, rating, rank, user_id, update.effective_user.id))
        connection.commit()
        insert_query = '''UPDATE do_task SET start_time = CURRENT_TIMESTAMP WHERE do_task_id = %s;'''
        cursor.execute(insert_query, (task_id,))
        connection.commit()
        select = '''SELECT task_user_id FROM do_task;'''
        cursor.execute(select)
        rex = cursor.fetchall()
        print(rex)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"""
Ссылка на задачу в LinkedIn: {linked_url}
Тип задания: {task_type}
            """
        )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Готовы ли выполнить эти задани?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    return CHOOSE_OPTION

async def finishing_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Задание выполнено"]]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="У вас есть час на выполнение заданий, если вы не выполните задания за указанное время, то будут наложены ограничения.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    time_delta = datetime.timedelta(seconds=20)
    context.job_queue.run_once(chek_chek, time_delta, chat_id=update.effective_chat.id, data=update)
    return CHOOSE_OPTION

async def chek_chek(context: ContextTypes.DEFAULT_TYPE):
    cursor = connection.cursor()
    job = context.job
    select_query = '''SELECT do_status FROM do_task WHERE task_user_id = %s;'''
    cursor.execute(select_query, (job.data.effective_user.id,))
    status = cursor.fetchone()[0]
    status = int(status)
    if status == 1:
        cursor.execute(f'''
            SELECT rate_calc_f, do_many, do_task_id FROM do_task WHERE task_user_id = {job.data.effective_user.id} ORDER BY start_time DESC LIMIT 5;
        ''')
        
        for rate in cursor.fetchall():
            user_rate = rate[0] 
            user_many = rate[1]
            task_id = rate[2]
            user_many -= 1
            insert_query2 = '''UPDATE add_task SET many = %s WHERE task_id = %s;'''
            cursor.execute(insert_query2, (user_many, task_id,))
            connection.commit()
            insert_query = '''UPDATE registr SET engage_rate = %s WHERE id = %s;'''
            cursor.execute(insert_query, (user_rate, job.data.effective_user.id,))
            connection.commit()

    elif status == 0:
        return await pull_back(job.data, context)

async def pull_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cursor = connection.cursor()
    cursor.execute(f'''
        SELECT do_task_id, do_task_type, do_linked_url, do_many, first_user_id
        FROM do_task
        WHERE now() - start_time >= INTERVAL '20 seconds' 
        AND task_user_id = {update.effective_user.id};
    ''')
    unfinished_tasks = cursor.fetchall()

    for do_task_id, do_task_type, do_linked_url, do_many, first_user_id in unfinished_tasks: #не аквтиные переменные висят тут на всякий случай, для расширения кода в будующем
        # Возвращаем задачу в общий пул
        cursor.execute('''
            DELETE FROM do_task WHERE do_task_id = %s;
        ''', (do_task_id,))
        connection.commit()

        # Увеличиваем рейтинг задачи на 10%
        cursor.execute('''
            UPDATE add_task
            SET rating = rating * 1.1
            WHERE task_id = %s;
        ''', (do_task_id,))
        connection.commit()

        # Увеличиваем рейтинг пользователя на 10%
        cursor.execute('''
            UPDATE registr
            SET engage_rate = engage_rate * 1.1
            WHERE id = %s;
        ''', (first_user_id,))
        connection.commit()

    # Возвращаем сообщение пользователю о возврате задач в пул
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Ваши невыполненные задачи были возвращены в общий пул, на вас наложенно ограничение, больше сегодня задач вы взять не сможите"
    )
    cursor = connection.cursor()
    cursor.execute("UPDATE add_task SET rating = r.engage_rate FROM registr r INNER JOIN add_task t ON r.id = t.user_id;")
    connection.commit()

    return await menu(update, context)

async def clear_task_limit():
    print(2)
    user_list = cursor.execute('SELECT id FROM registr WHERE status > 0').fetchall()
    user_list = [x[0] for x in user_list]
    cursor.execute(f'UPDATE registr SET status = 0 WHERE id in user_list')
    connection.commit()

def main():
    application = (
        ApplicationBuilder()
        .token("6833931155:AAH6tnqZbNcZs8FhnjmCSybO2hcHWYfpbKc")
        .build()
    )
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={CHOOSE_OPTION: [MessageHandler(filters.TEXT, choose_option)],
                CHOOSE_TYPE: [MessageHandler(filters.TEXT, choose_type)],
                LIKES: [MessageHandler(filters.TEXT, many_likes)],
                COMENTS: [MessageHandler(filters.TEXT, many_coments)],
                REPOSTS: [MessageHandler(filters.TEXT, many_reposts)],
                ADD_TASK: [MessageHandler(filters.TEXT, add_task)],
                CITY: [MessageHandler(filters.TEXT, city)],
                ROLE: [MessageHandler(filters.TEXT, role)],
                REGISTRATION_INFO: [MessageHandler(filters.TEXT, reg_info)],
                SKILLS: [MessageHandler(filters.TEXT, many_skills)],
                FOLLOWS: [MessageHandler(filters.TEXT, many_follows)]

                },
        fallbacks=[],
    )
    # schedule.every().day.at('14:13', tz=pytz.utc).do(clear_task_limit)
    schedule.every().day.at("15:40").do(clear_task_limit)
    print(1)

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    schedule.run_pending()
    main()
    