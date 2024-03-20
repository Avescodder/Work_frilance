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
import aiosqlite

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

MIDLE_OPTION, CHOOSE_OPTION = range(1, 3)

PAYMENT_PROVIDER_TOKEN = "390540012:LIVE:47983"

async def create_bd(loop):
    async with aiosqlite.connect('db.sqlite3', loop=loop) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS clients(
                            id INTEGER PRIMARY KEY,
                            status INTEGER,
                            day INTEGER);""")
        await db.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_board = [["Жертва","Спасатель","Агрессор"]]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"""🎁 Чек-лист по определению личной роли в треугольнике отношений в подарок 🎁

Привет, {update.effective_user.full_name}! Меня зовут Ирина Копылова. Я психолог, игропрактик, арт-терапевт.  ☘️

Как никто другой, я прекрасно знаю, как нам важно оставаться собой и не вовлекаться в те отношения, которые ведут к созависимости, разрушению личности и потери индивидуальности. 🌸

Треугольник Карпмана — именно так была названа ролевая модель поведения, которая не позволяет нам быть собой и максимально проявлять себя в этом мире.

Для того, чтобы стала понятна ваша роль в этих играх между людьми, я создала чек-листы, помогающие определить свое место в отношениях. Я дарю их вам. 🎁 

Чек-листы помогут определить основные признаки, по которым можно отнести себя к той или иной роли. 

Они подскажут, почему люди выбирают именно такую роль и как легко и достаточно быстро выйти из подобных отношений. 👌

Не важно, какое место вы занимаете в треугольнике. Важно, что здесь нет идеального образа.

Каждый игрок преследует свою цель и закрывает собственные проблемы. 

Просто выберите кнопку ниже, в соответствии с той ролью, в которой вы себя видите.

⏳ Не откладывайте свое тестирование «на потом», ведь чек-листы будут доступны только 48 часов!

Поехали ⬇️""",
        reply_markup=ReplyKeyboardMarkup(
            reply_board,
            resize_keyboard=True,
        ),
    )
    async with aiosqlite.connect('db.sqlite3') as db:
        async with db.execute('''SELECT id FROM clients WHERE id = ?''', (update.effective_user.id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return CHOOSE_OPTION
            else:
                await db.execute('''INSERT INTO clients (id) VALUES (?)''', (update.effective_user.id,))
                await db.commit()
                return CHOOSE_OPTION


async def choose_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_message.text == "Жертва":
        await progrev_func_gaidj(update, context)
        return
    
    if update.effective_message.text == "Спасатель":
        await progrev_func_gaids(update, context)
        return
    
    if update.effective_message.text == "Агрессор":
        return await progrev_func_gaida(update, context)
    
    if update.effective_message.text == "Получить путеводитель!":
        async with aiosqlite.connect('db.sqlite3') as db:
            await db.execute('''UPDATE clients SET status = ? WHERE id = ?''', (1, update.effective_user.id))
            await db.commit()
         
        return await payment_gaid(update, context)
    
    if update.effective_message.text == "Я ещё не созрел для решения":
        time_delta = datetime.timedelta(seconds=5)
        context.job_queue.run_once(progrev_after_gaid, time_delta, chat_id=update.effective_user.id, data=update)

    if update.effective_message.text == "Я ещё не принял решение":
        time_delta = datetime.timedelta(seconds=5)
        context.job_queue.run_once(buy_course, time_delta, chat_id=update.effective_chat.id, data=update)
    
    if update.effective_message.text == "ХОЧУ НА ПРОГРАММУ!":
        async with aiosqlite.connect('db.sqlite3') as db:
            await db.execute('''UPDATE clients SET status = ? WHERE id = ?''', (2, update.effective_user.id))
            await db.commit()

        return await payment_course(update, context)
    
    if update.effective_message.text == "Пока не готов к продолжению обучения":
        time_delta = datetime.timedelta(seconds=5)
        context.job_queue.run_once(progrev_after_course, time_delta, chat_id=update.effective_user.id, data=update)

    if update.effective_message.text == "Занять место в Программе!":
        async with aiosqlite.connect('db.sqlite3') as db:
            await db.execute('''UPDATE clients SET status = ? WHERE id = ?''', (2, update.effective_user.id))
            await db.commit()
        return await payment_course(update, context)
    
    if update.effective_message.text == "Хочу путеводитель!":
        async with aiosqlite.connect('db.sqlite3') as db:
            await db.execute('''UPDATE clients SET status = ? WHERE id = ?''', (1, update.effective_user.id))
            await db.commit()
        return await payment_gaid(update, context)


async def progrev_func_gaidj(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open("telegbot/courses/Example.pdf", "rb") as course:
        await context.bot.send_document(chat_id=update.message.chat.id, document=course)
    time_delta = datetime.timedelta(seconds=5)
    progrev_started = context.user_data.get("progrev_started")
    context.job_queue.run_once(sendmesage, time_delta, chat_id=update.effective_user.id, data=progrev_started)
    context.user_data["progrev_started"] = True

async def progrev_func_gaids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open("telegbot/courses/Example.pdf", "rb") as course:
        await context.bot.send_document(chat_id=update.message.chat.id, document=course)
    time_delta = datetime.timedelta(seconds=5)
    progrev_started = context.user_data.get("progrev_started")
    context.job_queue.run_once(sendmesage, time_delta, chat_id=update.effective_user.id, data=progrev_started)
    context.user_data["progrev_started"] = True

async def progrev_func_gaida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open("telegbot/courses/Example.pdf", "rb") as course:
        await context.bot.send_document(chat_id=update.message.chat.id, document=course)
    time_delta = datetime.timedelta(seconds=5)
    progrev_started = context.user_data.get("progrev_started")
    context.job_queue.run_once(sendmesage, time_delta, chat_id=update.effective_user.id, data=progrev_started)
    context.user_data["progrev_started"] = True

#фича
    
async def sendmesage(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    if job.data:
        return

    reply_keyb = [["Получить путеводитель!"],["Я ещё не созрел для решения"]]
    await context.bot.send_message(
        chat_id=job.chat_id,
        text="""90% людей играют свою роль на сцене Жизни. Как всё изменить? 

Вы уже скачали тот чек-лист, который наиболее близок к вам. А возможно, и все 3. 😇

Как вам живется в той роли, которую вы для себя выбрали? Наверняка не идеально. ⤵️

Проблема заключается в собственных невыраженных эмоциях и вытесненных чувствах:

    ⚠️ Жертва вытесняет агрессию. 
    ⚠️ Спасатель вытесняет бессилие. 
    ⚠️ Преследователь вытесняет слабость.

Я предлагаю не останавливаться!

Когда вы осознали свои роли — применяем принципы зеркального треугольника. 

Преследователь станет Уверенным, Спасатель — Заботливым, а Жертва перейдет в Беззащитного. 🔥🔥🔥

Благодаря специальным психологическим механизмам, человек справляется с собственными невыраженными чувствами, применяет новые модели поведения и строит новые реалистичные стандарты.

В результате, в отношениях появляется воздух и здоровые границы. ❤️

Определить кто ты, признаться себе, что это лишь прикрытие более глубоких процессов — классный шаг к себе настоящему и к выходу из зависимости от мнения и действий других людей. 🔥🔥🔥

Давайте выйдем из этих ролей как можно скорее.

Прямо сейчас, забирайте мой гайд-путеводитель по выходу из вашей Роли в треугольнике отношений. 🗺️

Просто жмите на кнопку ниже. 👇

Для нашего энергообмена и понимания вашего интереса к теме собственного личностного роста, я предлагаю отдать за него символическую сумму (цена стаканчика кофе). 🤗
                                    """,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyb, resize_keyboard=True, one_time_keyboard=True
        ),
    )



async def payment_gaid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    title = "Курс"
    description = "Payment Example"
    # select a payload just for you to recognize its the donation from your bot
    payload = "Custom-Payload"
    # In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
    currency = "RUB"
    # price in dollars
    price = 100
    # price * 100 so as to include 2 decimal points
    prices = [LabeledPrice("Test", price * 100)]

    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    await context.bot.send_invoice(
        chat_id,
        title,
        description,
        payload,
        PAYMENT_PROVIDER_TOKEN,
        currency,
        prices,
        need_email=True,
        send_email_to_provider=True,
        provider_data={
            "receipt": {
                "items": [
                    {
                        "description": title,
                        "quantity": "1.00",
                        "amount": {"value": str(price) + ".00", "currency": "RUB"},
                        "vat_code": 1,
                    },
                ]
            }
        },
    )
async def payment_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    title = "Payment Example"
    description = "Payment Example using python-telegram-bot"
    # select a payload just for you to recognize its the donation from your bot
    payload = "Custom-Payload"
    # In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
    currency = "RUB"
    # price in dollars
    price = 200
    # price * 100 so as to include 2 decimal points
    prices = [LabeledPrice("Test", price * 100)]

    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    await context.bot.send_invoice(
        chat_id,
        title,
        description,
        payload,
        PAYMENT_PROVIDER_TOKEN,
        currency,
        prices,
        need_email=True,
        send_email_to_provider=True,
        provider_data={
            "receipt": {
                "items": [
                    {
                        "description": title,
                        "quantity": "1.00",
                        "amount": {"value": str(price) + ".00", "currency": "RUB"},
                        "vat_code": 1,
                    },
                ]
            }
        },
    )


async def precheckout_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Answers the PreQecheckoutQuery"""
    query = update.pre_checkout_query
    if query.invoice_payload != "Custom-Payload":
        await query.answer(ok=False, error_message="Something went wrong...")
    else:
        await query.answer(ok=True)


async def successful_payment_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Confirms the successful payment."""
    async with aiosqlite.connect('db.sqlite3') as db:
        async with db.execute('''SELECT status FROM clients WHERE id = ?''',(update.effective_user.id,)) as cursor:
            async for answer in cursor:
                if answer[0] == 1:
                    await update.message.reply_text("Спасибо за покупку!")
                    with open("telegbot/courses/fae.pdf", "rb") as fae:
                        await context.bot.send_document(
                            chat_id=update.effective_chat.id,
                            document=fae
                            )
                    time_delta = datetime.timedelta(seconds=1)
                    context.job_queue.run_once(buy_course, time_delta, chat_id=update.effective_user.id, data=update)
                elif answer[0] == 2:
                    await update.message.reply_text("Спасибо за покупку!")
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="https://t.me/buddy_san_bot"
                    )


async def buy_course(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    replay_keyboard = [["ХОЧУ НА ПРОГРАММУ!"],["Пока не готов к продолжению обучения"]]
    await context.bot.send_message(
        chat_id=job.chat_id,
        text="""Лучшее, что вы можете сделать для себя — это начать поступательное движение для выхода из созависимых отношений!

Можно бесконечно искать способы решения своих проблем в интернете, или читать 100500 книг по психологии. 🫣

Но это не даст того результата, который вы ждете. Ведь каждая ситуация индивидуальна. 

Не может существовать универсального подхода!

Хотите навсегда прекратить сливать свои ресурсы в пустые отношения?

Здесь важно понимать свои истинные потребности, уметь отстаивать свои границы и распознавать границы другого. 

Вы уже сделали первый шаг и прошли бесплатное тестирование, а с помощью путеводителя узнали, что делать, чтобы навсегда убрать деструктивные роли из жизни.

В полной Программе мы будем работать на более глубоком уровне. 

У вас будут:  

    ✅ пошаговое руководство по выходу из созависимых отношений 
    ✅ техники развития самоосознания 
    ✅ инструменты для изменения поведенческих паттернов 
    ✅ практические упражнения для развития навыков здорового общения
    ✅ постоянная экспертная поддержка на всем прохождении Программы

⏳ Доступ к Программе откроется сразу после оплаты, а стоимость = одному походу в магазин за продуктами на 4 дня! 😍

Жмите на кнопку и присоединяйтесь к Программе «Seven Day». ❤️

                """,
        reply_markup=ReplyKeyboardMarkup(
            replay_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        ),
    )
    return CHOOSE_OPTION

async def progrev_after_gaid( context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    replay_keyboard = [["Хочу путеводитель!"],["Я ещё не принял решение"]]
    await context.bot.send_message(
        chat_id=job.chat_id,
        text=f"""{job.data.effective_user.full_name}, вы все еще не забрали свой путеводитель по выходу из Треугольника созависимости? Поторопитесь! ⚠️

Уверенность в себе, конструктивные решения, сохранение собственной энергии — первые и самые важные шаги в новой модели вашего поведения.

Как их сделать? Вам поможет этот гайд. 

❤️‍🔥 Не упускайте возможность получить ценные рекомендации от опытного психолога прямо сейчас! 
                """,
            reply_markup=ReplyKeyboardMarkup(
            replay_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        ),
    )
    
    return CHOOSE_OPTION

async def progrev_after_course( context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    replay_keyboard = [["Занять место в Программе!"]]
    await context.bot.send_message(
        chat_id=job.chat_id,
        text=f"""{job.data.effective_user.full_name}, ПЛАН ПО ВЫХОДУ ИЗ СИТУАЦИИ ЗДЕСЬ!

В качестве участников деструктивных отношений могут оказаться коллеги по работе, супруги, родители и даже дети. 

Как правило, в таких отношениях преобладают следующие паттерны поведения:

    ⚠️ возложение на партнера вины за то, что ваша жизнь протекает не так, как хотелось бы;
    ⚠️ вы не можете заниматься обычными делами, когда у близкого человека плохое настроение; у вас возникает стремление сделать все, чтобы устранить причину;
    ⚠️ вы боитесь обсудить возникающие проблемы с партнером, и в попытке понять ее суть и пути ее устранения делаете это с другими из чувства опасения его обидеть и расстроить;
    ⚠️ близкий, страдающий от зависимости, может обвинять вас в своих проблемах, а вы соглашаетесь, думая, что это поможет заслужить его любовь, поддержку и внимание;
    ⚠️ отсутствие желаемого внимания и помощи партнера заставляет думать, что вам следует стать более хорошим в отношениях.

Шаги, которые стоит предпринять, чтобы выйти из созависимых отношений и обрести себя, мы сделаем совместно на Программе «Seven Day»:

    ✅ окончательное отделение от прошлого
    ✅ работа над самооценкой и оценкой окружения
    ✅ корректировка эмоций
    ✅ защита своих ценностей
    ✅ избавление от манипуляций
    ✅ забота о себе
    ✅ обретение независимости
На ней вы узнаете как:

    📍 Стать социально активным и прекратить самоизоляцию от общества.
    📍 Научиться избегать конфликтов в семье и на работе или «гасить» их в самом начале.
    📍 Прекратить или нейтрализовать любые деструктивные отношения, а другие отношения направить в позитивное русло.
    📍 Жить своей жизнью, руководствуясь, прежде всего, собственными чувствами, интересами и потребностями.
    📍 Сбросить с себя бремя ответственности за жизнь Другого и нести ответственность прежде всего за себя и свое поведение.
    📍 Обрести уверенность в своей значимости для всего общества, а не только для одного человека, повысить свою самооценку и научиться конструктивному, позитивному мышлению.
    📍 Устанавливать и оберегать личные границы собственного Я в любых отношениях с другими людьми и социумом.

🔥 все видео-уроки в записи
🔥 доступ к Программе откроется сразу после оплаты
🔥 материалы доступны 6 месяцев 

Будь в их числе, приняв верное решение ⬇️


                """,
            reply_markup=ReplyKeyboardMarkup(
            replay_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        ),
    )
    return CHOOSE_OPTION

def main():

    application = (
        ApplicationBuilder()
        .token("6936836289:AAG7p5_f6MnipjOXiKDJfg2k7-YZPdt1SZs")
        .build()
    )
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={CHOOSE_OPTION: [MessageHandler(filters.TEXT, choose_option)]
                },
        fallbacks=[],
    )

    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))

    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback)
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_bd(loop))
    main()
