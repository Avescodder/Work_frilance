import aiosqlite

async def creation_database(path: str):
    async with aiosqlite.connect(path) as db:
        pass

# token