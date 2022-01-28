from bot import Bot
import sys
from dotenv import load_dotenv

sys.path.append("./")


def main():
    bot = Bot()
    for ext in [
        "cogs.raids.raid_cog",
        "cogs.time.time_cog",
        "cogs.calendar.calendar_cog",
        "cogs.setup.setup_cog",
    ]:
        bot.load_extension(ext)
    bot.run(bot.token)
    bot.logger.info("Shutting down.")


if __name__ == "__main__":
    main()
