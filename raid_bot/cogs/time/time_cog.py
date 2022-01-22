from discord.ext import commands

#TODO: comprehensive timezone setting and managing for users and servers
class TimeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_server_timezone(self):
        return self.bot.server_tz