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

PROGREV_FUNC, PAYMENT, EXCEPTION, CHOOSE_OPTION = range(1, 5)

PAYMENT_PROVIDER_TOKEN = "381764678:TEST:80237"

async def create_bd(loop):
    async with aiosqlite.connect('db.sqlite3', loop=loop) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS clients(
                            id INTEGER PRIMARY KEY,
                            status INTEGER,
                            day INTEGER);""")
        await db.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_board = [["Получить чек лист"]]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Приветствуем вас в нашем телеграм боте! Хотите начать обучение и получить эксклюзивные матриалы?",
        reply_markup=ReplyKeyboardMarkup(
            reply_board,
            resize_keyboard=True,
            one_time_keyboard=True,
            input_field_placeholder="Получите чек лист нажав всего одну кнопку",
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
    if update.effective_message.text == "Получить чек лист":
        return await progrev_func_gaid(update, context)
    
    if update.effective_message.text == "Да конечно! Приобрести гайд!":
        async with aiosqlite.connect('db.sqlite3') as db:
            await db.execute('''UPDATE clients SET status = ? WHERE id = ?''', (1, update.effective_user.id))
            await db.commit()
         
        return await payment_gaid(update, context)
    
    if update.effective_message.text == "Я ещё не созрел для решения":
        time_delta = datetime.timedelta(seconds=1)
        context.job_queue.run_once(progrev_after, time_delta, chat_id=update.effective_user.id)
    
    if update.effective_message.text == "Лучшее что я видел! Конечно хочу!":
        async with aiosqlite.connect('db.sqlite3') as db:
            await db.execute('''UPDATE clients SET status = ? WHERE id = ?''', (2, update.effective_user.id))
            await db.commit()

        return await payment_course(update, context)
    
    if update.effective_message.text == "Пока не готов к продолжению обучения":
        time_delta = datetime.timedelta(seconds=1)
        context.job_queue.run_once(progrev_after, time_delta, chat_id=update.effective_user.id)

    if update.effective_message.text == "Я поменял-а свое мнение, преобрету курс!":
        async with aiosqlite.connect('db.sqlite3') as db:
            await db.execute('''UPDATE clients SET status = ? WHERE id = ?''', (2, update.effective_user.id))
            await db.commit()
        return await payment_course(update, context)
    
    if update.effective_message == "Поменял-а свое мнение, преобрету гайд":
        async with aiosqlite.connect('db.sqlite3') as db:
            await db.execute('''UPDATE clients SET status = ? WHERE id = ?''', (1, update.effective_user.id))
            await db.commit()
        return await payment_gaid(update, context)


async def progrev_func_gaid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open("telegbot/courses/Example.pdf", "rb") as course:
        await context.bot.send_document(chat_id=update.message.chat.id, document=course)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Тут можно добавить описание чек листа",
    )
    time_delta = datetime.timedelta(seconds=1)
    context.job_queue.run_once(sendmesage, time_delta, chat_id=update.effective_user.id)


async def sendmesage(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    reply_keyb = [["Да конечно! Приобрести гайд!"],["Я ещё не созрел для решения"]]
    await context.bot.send_message(
        chat_id=job.chat_id,
        text="Уверенны в себе? Хотите приобрести гайд? ",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyb, resize_keyboard=True, one_time_keyboard=True
        ),
    )
    return CHOOSE_OPTION


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
                if answer == 1:
                    await update.message.reply_text("Спасибо за покупку!")
                    with open("telegbot/courses/fae.pdf", "pb") as fae:
                        await context.bot.send_document(
                            chat_id=update.effective_chat.id,
                            document=fae
                            )
                    time_delta = datetime.timedelta(seconds=1)
                    context.job_queue.run_once(buy_course, time_delta, chat_id=update.effective_user.id)
                elif answer == 2:
                    await update.message.reply_text("Спасибо за покупку!")
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="https://t.me/buddy_san_bot"
                    )


async def buy_course(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    replay_keyboard = [["Лучшее что я видел! Конечно хочу!"],["Пока не готов к продолжению обучения"]]
    await context.bot.send_message(
        chat_id=job.chat_id,
        text="Понравился гайд? Хотите приобрести курс?",
        reply_markup=ReplyKeyboardMarkup(
            replay_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        ),
    )
    return CHOOSE_OPTION

async def progrev_after( context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    replay_keyboard = [["Я поменял-а свое мнение, преобрету курс!"],["Поменял-а свое мнение, преобрету гайд"]]
    await context.bot.send_message(
        chat_id=job.chat_id,
        text="Текст для перепрогрева",
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
        states={CHOOSE_OPTION: [MessageHandler(filters.TEXT, choose_option)]},
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
