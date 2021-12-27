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

from raid_bot.models.raid_model import Raid
from raid_bot.models.raid_list_model import LIST_OF_RAIDS

sys.path.append("../")


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RaidCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("data/raid_options.json") as f:
            self.raid_options = json.load(f)
        self.raids = {}
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
        tank_button = Button(label="Tank", style=discord.ButtonStyle.blurple)
        dd_button = Button(label="DD", style=discord.ButtonStyle.red)
        heal_button = Button(label="Heal", style=discord.ButtonStyle.green)

        async def button_callback(interaction):
            edited_message = await interaction.response.edit_message()
            edited_raid = LIST_OF_RAIDS[edited_message.id]
            edited_raid.setup["Tanks"].append(interaction.username)
            embed_raid = self.build_raid_message(edited_raid)
            
        tank_button.callback = button_callback

        raid = Raid(name, mode, description, time)

        raid_embed = self.build_raid_message(raid)
        view = self.build_raid_view(tank_button, dd_button, heal_button)
        message = await ctx.respond(embed=raid_embed, view=view)
        LIST_OF_RAIDS[message.id] = raid

    def build_raid_message(self, raid):
        embed_title = f"{raid.name} {raid.mode}\n<t:{raid.time}:F>"
        embed = discord.Embed(title=embed_title, description=raid.description, colour=0x4B34EF)

        for role in raid.roster:
            current = len(raid.setup[role])
            limit = raid.roster[role]
            field_string = f"{role} {current}/{limit}"
            embed.add_field(name=field_string, value='\u200b')
        return embed

    def build_raid_view(self, tank_button, dd_button, heal_button):
        view = View()
        view.add_item(tank_button)
        view.add_item(dd_button)
        view.add_item(heal_button)

        return view


def setup(bot):
    bot.add_cog(RaidCog(bot))
    logger.info("Loaded Raid Cog.")
