import sys
import logging
import datetime
from typing import List
import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from raid_bot.models.raid_list_model import LIST_OF_RAIDS
from raid_bot.models.raid_list_model import Raid

sys.path.append("../")


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RaidCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(guild_ids=[902671732987551774])
    async def calendar(self, ctx):
        embed = self.build_calendar_embed()
        ctx.respond(embed=embed)

    def build_calendar_embed(self):

        raids: List[Raid] = LIST_OF_RAIDS
        title = _("Scheduled runs:")
        desc = _("Click the link to sign up!")
        embed = discord.Embed(
            title=title, description=desc, colour=discord.Colour(0x3498DB)
        )
        for raid in raids[:20]:
            timestamp = int(raid.time)
            msg = "[{name} {mode}](<https://discord.com/channels/{guild}/{channel}/{msg}>)\n".format(
                guild=902671732987551774,
                channel=raid[0],
                msg=raid[1],
                name=raid.name,
                mode=raid.mode,
            )
            embed.add_field(name=f"<t:{timestamp}:F>", value=msg, inline=False)
        embed.set_footer(text=_("Last updated"))
        embed.timestamp = datetime.now()
        return embed
