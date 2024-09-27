import json
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)
from telegram import ReplyKeyboardMarkup
import datetime
import pytz
import aiosqlite


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


CHOOSE_OPTION = range(1, 2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with aiosqlite.connect("db.sqlite3") as db:
        async with db.execute(
            """SELECT status FROM clients WHERE id = ?""", (update.effective_user.id,)
        ) as cursor:
            async for row in cursor:
                status = row[0]
                if status == 1:
                    replay_keyboard = [["Далее"]]
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="Приветствую вас на нашем курсе, давайте приступим к обучению!!!",
                        reply_markup=ReplyKeyboardMarkup(
                            replay_keyboard,
                            resize_keyboard=True,
                            one_time_keyboard=True,
                        ),
                    )
                    return CHOOSE_OPTION
                else:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="У вас нет доступа, не заплатили",
                    )


async def choose_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with aiosqlite.connect("db.sqlite3") as db:
        async with db.execute(
            """SELECT day FROM clients WHERE id = ?""", (update.effective_user.id,)
        ) as cursor:
            async for row in cursor:
                day = str(row[0])
    with open("telegram_work_freelance/прогрев.txt", "r") as f:
        days = json.load(f)
    if update.effective_message.text == "Далее":
        async with aiosqlite.connect("db.sqlite3") as db:
            await db.execute(
                """UPDATE clients SET day = ? WHERE id = ?""",
                (1, update.effective_user.id),
            )
            await db.commit()
        return await send_video1(update, context)

    elif update.effective_message.text == days[day]["ans1"]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Молодец, правильно ответил"
        )
        if day == "1":
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Следующие видео с заданием придет автоматически через 12 часов",
            )
            async with aiosqlite.connect("db.sqlite3") as db:
                await db.execute(
                    """UPDATE clients SET day = ? WHERE id = ?""",
                    (
                        2,
                        update.effective_user.id,
                    ),
                )
                await db.commit()
            time_delta = datetime.timedelta(minutes=1)
            context.job_queue.run_once(
                send_video2, time_delta, chat_id=update.effective_chat.id, data=update
            )
        elif day == "2":
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Следующие видео с заданием придет автоматически через 12 часов",
            )
            async with aiosqlite.connect("db.sqlite3") as db:
                await db.execute(
                    """UPDATE clients SET day = ? WHERE id = ?""",
                    (
                        3,
                        update.effective_user.id,
                    ),
                )
                await db.commit()
            time_delta = datetime.timedelta(minutes=1)
            context.job_queue.run_once(
                send_video3, time_delta, chat_id=update.effective_chat.id, data=update
            )
        elif day == "3":
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Поздравляю вас, вы завершили периуд заданий с видео, теперь будут только текстовые задания с тестами на закрепление материала",
            )
            async with aiosqlite.connect("db.sqlite3") as db:
                await db.execute(
                    """UPDATE clients SET day = ? WHERE id = ?""",
                    (
                        4,
                        update.effective_user.id,
                    ),
                )
                await db.commit()
            time_delta = datetime.timedelta(minutes=1)
            context.job_queue.run_once(
                send_task, time_delta, chat_id=update.effective_chat.id, data=update
            )
        elif day == "4":
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Следующие текстовое задание придет через 12 часов",
            )
            async with aiosqlite.connect("db.sqlite3") as db:
                await db.execute(
                    """UPDATE clients SET day = ? WHERE id = ?""",
                    (
                        5,
                        update.effective_user.id,
                    ),
                )
                await db.commit()
            time_delta = datetime.timedelta(minutes=1)
            context.job_queue.run_once(
                send_task, time_delta, chat_id=update.effective_chat.id, data=update
            )
        elif day == "5":
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Следующие текстовое задание придет через 12 часов",
            )
            async with aiosqlite.connect("db.sqlite3") as db:
                await db.execute(
                    """UPDATE clients SET day = ? WHERE id = ?""",
                    (
                        6,
                        update.effective_user.id,
                    ),
                )
                await db.commit()
            time_delta = datetime.timedelta(minutes=1)
            context.job_queue.run_once(
                send_task, time_delta, chat_id=update.effective_chat.id, data=update
            )
        elif day == "6":
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Следующие текстовое задание придет через 12 часов",
            )
            async with aiosqlite.connect("db.sqlite3") as db:
                await db.execute(
                    """UPDATE clients SET day = ? WHERE id = ?""",
                    (
                        7,
                        update.effective_user.id,
                    ),
                )
                await db.commit()
            time_delta = datetime.timedelta(minutes=1)
            context.job_queue.run_once(
                send_task, time_delta, chat_id=update.effective_chat.id, data=update
            )
        elif day == "7":
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="поздравляю вас с прохождением нашего курса",
            )

    elif update.effective_message.text == days[day]["ans2"]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="ответ не правильный"
        )
        time_delta = datetime.timedelta(seconds=2)
        context.job_queue.run_once(
            send_task, time_delta, chat_id=update.effective_chat.id, data=update
        )
    elif update.effective_message.text == days[day]["ans3"]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="ответ не правильный"
        )
        time_delta = datetime.timedelta(seconds=2)
        context.job_queue.run_once(
            send_task, time_delta, chat_id=update.effective_chat.id, data=update
        )
    elif update.effective_message.text == days[day]["ans4"]:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="ответ не правильный"
        )
        time_delta = datetime.timedelta(seconds=2)
        context.job_queue.run_once(
            send_task, time_delta, chat_id=update.effective_chat.id, data=update
        )


async def send_video1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open("telegbot/courses/GDUJsxkZPOjKMc4CALk-xXVKZRBIbmdjAAAF.mp4", "rb") as f:
        await context.bot.send_video(chat_id=update.effective_chat.id, video=f)
    time_delta = datetime.timedelta(seconds=15)
    context.job_queue.run_once(
        send_task, time_delta, chat_id=update.effective_chat.id, data=update
    )


async def send_video2(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    update = job.data
    with open("telegbot/courses/GDUJsxkZPOjKMc4CALk-xXVKZRBIbmdjAAAF.mp4", "rb") as f:
        await context.bot.send_video(chat_id=job.chat_id, video=f)
    time_delta = datetime.timedelta(seconds=15)
    context.job_queue.run_once(
        send_task, time_delta, chat_id=update.effective_chat.id, data=job.data
    )


async def send_video3(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    update = job.data
    with open("telegbot/courses/GDUJsxkZPOjKMc4CALk-xXVKZRBIbmdjAAAF.mp4", "rb") as f:
        await context.bot.send_video(chat_id=job.chat_id, video=f)
    time_delta = datetime.timedelta(second=15)
    context.job_queue.run_once(
        send_task, time_delta, chat_id=update.effective_chat.id, data=job.data
    )


async def send_task(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    with open("telegram_work_freelance/прогрев.txt", "r") as f:
        days = json.load(f)
        async with aiosqlite.connect("db.sqlite3") as db:
            async with db.execute(
                """SELECT day FROM clients WHERE id = ?""",
                (job.data.effective_user.id,),
            ) as cursor:
                async for day in cursor:
                    day_sh = str(day[0])
                    question = days[day_sh]["question"]
                    ans1 = days[day_sh]["ans1"]
                    ans2 = days[day_sh]["ans2"]
                    ans3 = days[day_sh]["ans3"]
                    ans4 = days[day_sh]["ans4"]
    reply_keyboard = [[ans1, ans2], [ans3, ans4]]
    await context.bot.send_message(
        chat_id=job.chat_id,
        text=question,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, resize_keyboard=True, one_time_keyboard=True
        ),
    )
    return CHOOSE_OPTION


def main():
    application = (
        ApplicationBuilder()
        .token("6767470341:AAFmw1Ays8MHY8kK--lmkU82vxElNUhcTu8")
        .build()
    )
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={CHOOSE_OPTION: [MessageHandler(filters.TEXT, choose_option)]},
        fallbacks=[],
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
