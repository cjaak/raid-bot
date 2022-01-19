import datetime

import dateparser
from discord.ext import commands
import discord
from discord.ext.commands import Context
from discord.ext.commands.converter import T_co


class Time(commands.Converter):
    async def convert(self, ctx: Context, argument: str) -> T_co:
        return self.converter(ctx.bot, ctx.guild.id, ctx.author.id, argument)

    @staticmethod
    def converter(bot, guild_id, author_id, argument):
        time_cog = bot.get_cog('TimeCog')
        argument_lower = argument.lower()
        parse_settings = {'PREFER_DATES_FROM': 'future'}
        server = _('server')
        if server in argument_lower:
            # Strip off server (time) and return as server time
            argument = argument_lower.partition(server)[0]
            parse_settings['TIMEZONE'] = time_cog.get_server_timezone()
            parse_settings['RETURN_AS_TIMEZONE_AWARE'] = True
        time = dateparser.parse(argument, settings=parse_settings)
        if time is None:
            raise commands.BadArgument(_("Failed to parse time: "), argument)
        timestamp = int(time.timestamp())

        # Avoid scheduling event in the past
        if "now" in argument_lower:
            return timestamp + 5
        return timestamp


