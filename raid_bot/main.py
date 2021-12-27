from bot import Bot
import sys
from dotenv import load_dotenv

sys.path.append("./")

def main():
    bot = Bot()
    for ext in ["cogs.raid"]:
        bot.load_extension(ext)
    bot.run(bot.token)
    bot.logger.info("Shutting down.")


if __name__ == "__main__":
    main()
