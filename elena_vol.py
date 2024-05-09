#ключ доступа клиента от 11:32 09/05/24: UA1IVRK5Qhm6LWEu9iuodgF_qs1Tzk-3JuyTKtWf
#client_id = I6PdLx7Wy21W2Upg6gvt
#client_secret = lO1R355g_yKz5ki3B0_EVYLYU0BN6omV5i1_alyu
import requests
import schedule
import time
client_id = "I6PdLx7Wy21W2Upg6gvt"
client_secret = "lO1R355g_yKz5ki3B0_EVYLYU0BN6omV5i1_alyu"
api_token = "UA1IVRK5Qhm6LWEu9iuodgF_qs1Tzk-3JuyTKtWf"
def get_temporary_access_token(client_id, client_secret):
    url = "https://api.avito.ru/token/"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # Проверка на успешный ответ
        global api_token
        api_token = response.json().get("access_token")
    except requests.HTTPError as err:
        print("Ошибка при получении временного ключа доступа:", err)

# Пример использования функции для получения временного ключа доступа

def get_chat_info(api_token, client_id):
    url = "https://api.avito.ru/messenger/v2/accounts/{client_id}/chats"
    headers = {
        "messenger" : "read",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    data = {
        "user_id" : client_id
    }
    try:
        response = requests.get(url, headers=headers, data=data)
        response.raise_for_status()  # Проверка на успешный ответ
        chats_info = response.json()
        return chats_info
    except requests.HTTPError as err:
        print("Ошибка при получении информации о чатах:", err)


def main():
    schedule.every(24).hours.do(get_temporary_access_token, client_id, client_secret)
    print(get_chat_info(api_token, client_id))

if __name__ == "__main__":
    main()
    while True:
        schedule.run_pending()
        time.sleep(1)