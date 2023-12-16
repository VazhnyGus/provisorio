import asyncio

from db import initiate_db
from tgbot import main


if __name__ == "__main__":
    initiate_db()
    asyncio.run(main())
