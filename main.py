import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

from userbot import start_userbot
from control_bot import start_control_bot

async def main():
    await asyncio.gather(
        start_userbot(),
        start_control_bot()
    )

if __name__ == '__main__':
    asyncio.run(main())