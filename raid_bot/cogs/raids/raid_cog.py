from discord import Interaction
from discord.ext import commands
import discord
import asyncio

from discord.ui import Button, View
from discord.commands import (
    slash_command,
    Option,
)  # Importing the decorator that makes slash commands.
import logging
import json
import datetime
import sys

from raid_bot.cogs.raids.raid_view import RaidView
from raid_bot.cogs.raids.raid_message_builder import build_raid_message
from raid_bot.models.raid_model import Raid
from raid_bot.models.raid_list_model import LIST_OF_RAIDS
from raid_bot.cogs.time.time import Time
from raid_bot.database import insert_raid, create_table

sys.path.append("../")


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
RAIDS = [
    "Terror from Beyond",
    "Scum and Villainy",
    "Temple of Sacrifice",
    "The Ravagers",
    "Dread Fortress",
    "Dread Palace",
]


class RaidCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = self.bot.conn

        create_table(self.conn, "raid")
        create_table(self.conn, "assign")

    @slash_command(
        guild_ids=[902671732987551774]
    )  # Create a slash command for the supplied guilds.
    async def raid(
        self,
        ctx,
        name: Option(
            str,
            "Choose the Raid",
            choices=RAIDS,
        ),
        mode: Option(str, "Choose the mode", choices=["SM", "HM", "NIM"]),
        time: Option(str, "Set the time"),
        description: Option(str, "Description", required=False),
        setup: Option(str, "Choose a saved setup", required=False, choices=[])
    ):
        """Schedules a raid"""
        timestamp = Time().converter(self.bot, time)

        post = await ctx.send("\u200B")

        raid_id = int(post.id)

        insert_raid(
            self.conn,
            raid_id,
            ctx.channel.id,
            ctx.guild_id,
            ctx.author.id,
            name,
            mode,
            description,
            timestamp,
            setup
        )

        raid_embed: discord.Embed = build_raid_message(self.conn, raid_id)
        await post.edit(embed=raid_embed, view=RaidView(self.conn))

        # workaround because `respond` seems to be required.
        dummy = await ctx.respond("\u200B")
        await dummy.delete_original_message(delay=None)


def setup(bot):
    bot.add_cog(RaidCog(bot))
    logger.info("Loaded Raid Cog.")
