from discord import Interaction
from discord.ext import commands
import discord
import asyncio

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
from raid_bot.cogs.raids.raid_message_builder import build_raid_message
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
        timestamp: Option(str, "Set the time"),
        description: Option(str, "Description", required=False)
    ):
        """Schedules a raid"""
        post = await ctx.send('\u200B')

        self.bot.logger.info(ctx)

        raid_id = post.id
        raid = Raid(name, mode, description, timestamp)

        raid_embed = build_raid_message(raid)
        await post.edit(embed=raid_embed, view=RaidView())

        LIST_OF_RAIDS[raid_id] = raid

        # workaround because respond is required at least once.
        await ctx.respond('\u200B')


    def dump(self, obj):
        for attr in dir(obj):
            self.bot.logger.info("obj.%s = %r" % (attr, getattr(obj, attr)))



def setup(bot):
    bot.add_cog(RaidCog(bot))
    logger.info("Loaded Raid Cog.")

