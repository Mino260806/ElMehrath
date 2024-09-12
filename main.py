import os

from bot.elmehrath import ElMehrathBot
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv(".env")
    token = os.environ["ELMEHRATH_TOKEN"]

    bot = ElMehrathBot()
    bot.run(token)
