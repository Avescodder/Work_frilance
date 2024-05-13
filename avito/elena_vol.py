#ключ доступа клиента от 11:32 09/05/24: UA1IVRK5Qhm6LWEu9iuodgF_qs1Tzk-3JuyTKtWf
#client_id = I6PdLx7Wy21W2Upg6gvt
#client_secret = lO1R355g_yKz5ki3B0_EVYLYU0BN6omV5i1_alyu
import aiohttp
import asyncio

client_id = "0j6FFI-Ii1uyp8Nm_4i_"
user_id = "103286876"
client_secret = "uyf8aP2x3wFVg7SKf8_XjBjG2LdZlDcDC-RCX0_x"
api_token = "UA1IVRK5Qhm6LWEu9iuodgF_qs1Tzk-3JuyTKtWf"


async def get_temporary_access_token(client_id, client_secret):
    url = "https://api.avito.ru/token/"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.post(url, headers=headers, data=data) as response:
            response.raise_for_status()  # Проверка на успешный ответ
            global api_token
            api_token = (await response.json()).get("access_token")
            print(api_token)
            return api_token


async def get_chat_info(api_token, client_id):
    url = f"https://api.avito.ru/messenger/v2/accounts/{user_id}/chats"
    headers = {
        "messenger": "read",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    data = {
        "user_id": user_id,
        "unread_only": "true"
    }

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(url, headers=headers, params=data) as response:
            response.raise_for_status()  # Проверка на успешный ответ
            chats_info = await response.json()
            chat_ids = []
            for chat in chats_info["chats"]:  # Обращаемся к значению ключа "chats"
                chat_ids.append(chat['id'])
            return chat_ids


async def get_messages(api_token, user_id, chat_ids):
    messages_dict = {}
    for chat_id in chat_ids:
        url = f"https://api.avito.ru/messenger/v3/accounts/{user_id}/chats/{chat_id}/messages/"
        headers = {
            "Authorization": f"Bearer {api_token}"
        }

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()  # Проверка на успешный ответ
                messages_info = await response.json()
                messages_dict[chat_id] = messages_info
    return messages_dict


async def send_question(api_token, user_id, chat_id, question_number, question_text):
    url = f"https://api.avito.ru/messenger/v1/accounts/{user_id}/chats/{chat_id[0]}/messages"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    data = {
        "message": {
            "text": f"Вопрос {question_number}: {question_text}"
        },
        "type": "text"
    }

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.post(url, headers=headers, json=data) as response:
            response.raise_for_status()  # Проверка на успешный ответ
            print(f"Сообщение с вопросом {question_number} отправлено успешно в чат {chat_id}")
            return True


def process_answer(answer):
    # Здесь вы можете обработать ответ пользователя и выполнить соответствующие действия
    if answer == "1":
        print("Пользователь ответил на первый вопрос")
    elif answer == "2":
        print("Пользователь ответил на второй вопрос")
    else:
        print("Пользователь ответил на другой вопрос")


async def main():
    # async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
    #     while True:
            print(await get_temporary_access_token(client_id, client_secret))
    #         chat_ids = await get_chat_info(api_token, client_id)
    #         print(chat_ids)
    #         tasks = []
    #         for chat_id in chat_ids:
    #             tasks.append(send_question(api_token, user_id, [chat_id], 1, "Какой ваш любимый цвет? (1. Красный, 2. Синий, 3. Зеленый)"))
    #         await asyncio.gather(*tasks)
    #         messages_dict = await get_messages(api_token, user_id, chat_ids)
    #         for chat_id, messages_info in messages_dict.items():
    #             if "messages" in messages_info and messages_info["messages"]:
    #                 if "text" in messages_info["messages"][0]:
    #                     process_answer(messages_info["messages"][0]["text"])
    #                 else:
    #                     print("В первом сообщении нет текста")
    #             else:
    #                 print("Нет сообщений в чате")

    #         await asyncio.sleep(60)  # Пауза между сканированием чатов


if __name__ == "__main__":
    asyncio.run(main())

