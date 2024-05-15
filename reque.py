# import time
# import requests


# client_id = "I6PdLx7Wy21W2Upg6gvt"
# client_secret = "lO1R355g_yKz5ki3B0_EVYLYU0BN6omV5i1_alyu"


# # url = "https://api.avito.ru/token/"
# # headers = {
# #     "Content-Type": "application/x-www-form-urlencoded"
# # }
# # data = {
# #     "client_id": client_id,
# #     "client_secret": client_secret,
# #     "grant_type": "client_credentials"
# # }

# # response = requests.post(url, headers=headers, data=data)
# # response.raise_for_status()
# # print(response.text)

# api_token = 'F09DyGRrTjOKiKNXU_n3NgO5_6EEG6iqBhnJ5eCu'

# # url = f"https://api.avito.ru/core/v1/accounts/self"
# url = f"https://api.avito.ru/messenger/v2/accounts/103286876/chats"
# headers = {'Authorization': f'Bearer {api_token}'}
# response = requests.get(url, headers=headers)
# # time.sleep(1)
# response.raise_for_status()
# print(response.text)

try:
    print(int('a'))
    print(1)
    print(int('b'))
except Exception:
    continue