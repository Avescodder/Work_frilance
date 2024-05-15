import aiosqlite

async def creation_database(path: str):
    async with aiosqlite.connect(path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS dialogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author_id TEXT NOT NULL,
                status INTEGER NOT NULL,
                chat_id TEXT NOT NULL
            )
        """)
        await db.commit()
        

