from discord.ext import commands
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# TODO: comprehensive timezone setting and managing for users and servers
class TimeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_server_timezone(self):
        return self.bot.server_tz


def setup(bot):
    bot.add_cog(TimeCog(bot))
    logger.info("Loaded Time Cog.")
