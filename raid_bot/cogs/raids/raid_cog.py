from discord.ext import commands
from typing import Dict
import discord

from discord.ui import Button, View
from discord.commands import (
    slash_command,
    Option
)  # Importing the decorator that makes slash commands.
import logging
import json
import datetime
import sys

from raid_bot.cogs.raids.raid_view import RaidView
from raid_bot.models.raid_model import Raid
from raid_bot.models.raid_list_model import LIST_OF_RAIDS

sys.path.append("../")


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RaidCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @slash_command(
        guild_ids=[902671732987551774]
    )  # Create a slash command for the supplied guilds.
    async def raid(
        self,
        ctx,
        name: Option(
            str,
            "Choose the Raid",
            choices=[
                "Terror from Beyond",
                "Scum and Villainy",
                "Temple of Sacrifice",
            ],
        ),
        mode: Option(str, "Choose the mode", choices=["sm", "hm", "nim"]),
        time: Option(str, "Set the time"),
        description: Option(str, "Description")
    ):
        """Schedules a raid"""

        raid = Raid(name, mode, description, time)

        raid_embed = self.build_raid_message(raid)
        message = await ctx.respond(embed=raid_embed, view=RaidView())
        LIST_OF_RAIDS[message.id] = raid

        print(LIST_OF_RAIDS)

    def build_raid_message(self, raid):
        embed_title = f"{raid.name} {raid.mode}\n<t:{raid.time}:F>"
        embed = discord.Embed(title=embed_title, description=raid.description, colour=0x4B34EF)

        for role in raid.roster:
            current = len(raid.setup[role])
            limit = raid.roster[role]
            field_string = f"{role} {current}/{limit}"
            embed.add_field(name=field_string, value='\u200b')
        return embed



def setup(bot):
    bot.add_cog(RaidCog(bot))
    logger.info("Loaded Raid Cog.")
