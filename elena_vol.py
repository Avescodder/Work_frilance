import requests
def get_chats_info():
    url = "https://api.avito.ru/messenger/v2/accounts/{user_id}/chats"
    headers = {
        "Content-Type": "application/json",
        "messenger":"read",
        "Authorization": "2GfAPOiQTNiQ7YQAxyjTZgAAA5uGsXXWZFwa69S3"
        
    }



    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверка на успешный ответ
        chats_info = response.json()
        return chats_info
    except requests.HTTPError as e:
        print("Ошибка при получении информации о чатах:", e)

chats_info = get_chats_info()
print(chats_info)