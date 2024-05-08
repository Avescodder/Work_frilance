import requests
# URL для API Avito
url = "https://api.avito.ru/messenger/v2/accounts/{I6PdLx7Wy21W2Upg6gvt}/chats"

# Заголовки HTTP-запроса (необходимо указать заголовок Content-Type для JSON)
headers = {
    "Content-Type": "application/json",
    "Authorization URL": "https://avito.ru/oauth",
    "Authorization": "Bearer lO1R355g_yKz5ki3B0_EVYLYU0BN6omV5i1_alyu",
    "Token URL": "https://api.avito.ru/token",
    "messenger":"read",
    "user":"read"
}

# JSON-данные для отправки
def send_data():
    data = {
      
    }

    # Отправка POST-запроса с данными в формате JSON
    response = requests.post(url, headers=headers, json=data)

    # Проверка статуса ответа
    if response.status_code == 200:
        print("Запрос успешно выполнен!")
        print("Ответ сервера:", response.json())
    else:
        print("Ошибка при выполнении запроса:", response.text)
def get_chats_info():
    params = {
        "user_id" : "I6PdLx7Wy21W2Upg6gvt"
    }

# Отправка GET-запроса с параметрами
    response = requests.get(url, headers=headers, params=params)

   

# Проверка статуса ответа
    if response.status_code == 200:
        chats_info = response.json()
        return chats_info
    else:
        print("Ошибка при получении информации о чатах:", response.text)

chats_info = get_chats_info()
print(chats_info)