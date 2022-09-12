import pytz
from discord import slash_command, Option
from discord.ext import commands
import logging

from raid_bot.database import (
    insert_or_replace_personal_timezone,
    update_server_timezone,
    select_server_timezone,
    select_personal_timezone,
    create_table,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TimeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = bot.conn

        create_table(self.bot.conn, "timezone")

    @slash_command()
    async def set_personal_timezone(self, ctx, timezone: Option(str, "Set timezone")):
        conn = self.conn
        try:
            tz = pytz.timezone(timezone)
        except pytz.UnknownTimeZoneError as e:
            content = f"{e} is not a valid time zone!"
        else:
            tz = str(tz)
            res = insert_or_replace_personal_timezone(conn, ctx.user.id, tz)
            if res:
                conn.commit()
                content = f"Set your time zone to {tz}."
            else:
                content = "An error occurred."
        await ctx.respond(content)

    @slash_command()
    async def set_server_timezone(self, ctx, timezone: Option(str, "set timezone")):
        if not ctx.user.guild_permissions.administrator:
            content = "You must be a server admin to change the server time zone."
            await ctx.respond(content)
            return
        conn = self.conn
        try:
            tz = pytz.timezone(timezone)
        except pytz.UnknownTimeZoneError as e:
            content = f"{e} is not a valid time zone!"
        else:
            tz = str(tz)
            update_server_timezone(conn, ctx.guild_id, tz)
            conn.commit()
            content = f"Set default time zone to {tz}."
        await ctx.respond(content)

    def get_server_timezone(self, guild_id):
        conn = self.conn
        result = select_server_timezone(conn, guild_id)
        if result is None:
            result = self.bot.server_tz
        return result

    def get_user_timezone(self, user_id, guild_id):
        conn = self.conn
        result = select_personal_timezone(conn, user_id)
        if result is None:
            result = self.get_server_timezone(guild_id)
        return result


def setup(bot):
    bot.add_cog(TimeCog(bot))
    logger.info("Loaded Time Cog.")
