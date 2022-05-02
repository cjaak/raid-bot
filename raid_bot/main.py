import sys

from bot import Bot

sys.path.append("./")


def main():
    bot = Bot()
    for ext in [
        "cogs.time.time_cog",
        "cogs.calendar.calendar_cog",
        "cogs.raids.raid_cog",
        "cogs.setup.setup_cog",
        "cogs.utility.utility_cog",
        "cogs.poll.poll_cog",
    ]:
        bot.load_extension(ext)
    bot.run(bot.token)
    bot.logger.info("Shutting down.")


if __name__ == "__main__":
    main()
