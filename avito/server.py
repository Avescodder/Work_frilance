import aiohttp
from aiohttp import web
import asyncio
import json
from dotenv import load_dotenv
import os
from elena_vol import get_temporary_access_token

load_dotenv()

connector = aiohttp.TCPConnector(ssl=False)

ngrok_url = 'https://18a0-5-228-89-161.ngrok-free.app'

async def register_avito_webhook(api_token):
    url = "https://api.avito.ru/messenger/v3/webhook"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "url": f"{ngrok_url}/avito_webhook",
    }

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.post(url, headers=headers, json=payload) as response:
            response.raise_for_status()
            if response.status == 200:
                print('Вебхук зарегистрирован')
            else:
                print(response.status)
                print(await response.text())

async def handle_avito_webhook(request):
    data = await request.json()
    data_json = json.loads(data)
    # вызов своей функции, которая работает с сообщениями

    # if который проверяет author_id от 2го аккаунта
    print(json.dumps(data, indent=2))
    return web.Response(status=200, text='ok')


async def main():
    api_token = os.getenv("API_TOKEN")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    print(client_id, client_secret)
    if api_token is None:
        api_token = await get_temporary_access_token(client_id, client_secret)
        print(f"api_token: {api_token}")
        os.environ["API_TOKEN"] = api_token

    app = web.Application()
    app.router.add_post('/avito_webhook' , handle_avito_webhook)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    await register_avito_webhook(api_token, client_secret)

    # Keep the server running
    print("Server started at http://localhost:8080")
    while True:
        await asyncio.sleep(3600)  # Sleeps for 1 hour

if __name__ == "__main__":
    asyncio.run(main())