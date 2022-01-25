import sys
import logging
import datetime
from typing import List
import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from raid_bot.models.raid_list_model import Raid
from raid_bot.database import select_all_raids_by_guild_id

sys.path.append("../")


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CalendarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = bot.conn

    @slash_command(guild_ids=[902671732987551774])
    async def calendar(self, ctx):
        embed = self.build_calendar_embed(ctx.guild_id)
        ctx.respond(embed=embed)

    def build_calendar_embed(self, guild_id: int):

        raids: List[Raid] = [
            Raid(list_item) for list_item in select_all_raids_by_guild_id(self.conn, guild_id)
        ]
        title: str = _("Scheduled runs:")
        desc: str = _("Click the link to sign up!")
        embed: discord.Embed = discord.Embed(
            title=title, description=desc, colour=discord.Colour(0x3498DB)
        )
        for raid in raids[:20]:
            timestamp = int(raid.time)
            msg = "[{name} {mode}](<https://discord.com/channels/{guild}/{channel}/{msg}>)\n".format(
                guild=guild_id,
                channel=raid.channel_id,
                msg=raid.raid_id,
                name=raid.name,
                mode=raid.mode,
            )
            embed.add_field(name=f"<t:{timestamp}:F>", value=msg, inline=False)
        embed.set_footer(text=_("Last updated"))
        embed.timestamp = datetime.datetime.utcnow()
        return embed

def setup(bot):
    bot.add_cog(CalendarCog(bot))
    logger.info("Loaded Calendar Cog.")