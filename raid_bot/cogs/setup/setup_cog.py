from discord.ui import Button, View
from typing import List
import discord
import logging
from discord.ext import commands
from discord.commands import (
    slash_command,
    Option,
)  # Importing the decorator that makes slash commands.
import logging
import json
import datetime
import sys

from raid_bot.cogs.setup.setup_view import SetupView

sys.path.append("../")

from raid_bot.models.sign_up_options import SignUpOptions, EMOJI
from raid_bot.models.setup_player_model import SetupPlayer
from raid_bot.database import (
    insert_or_replace_setup,
    select_all_players_for_setup,
    create_table,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = self.bot.conn

        create_table(self.conn, "setup")
        create_table(self.conn, "setup_players")

    @slash_command(guild_ids=[902671732987551774, 826561483731107891])
    async def setup(self, ctx, name: Option(str, "Name this setup.")):

        post = await ctx.send("\u200B")
        setup_id = int(post.id)

        insert_or_replace_setup(self.conn, setup_id, ctx.guild_id, name)
        self.conn.commit()

        embed: discord.Embed = self.build_setup_embed(setup_id, name)

        await post.edit(embed=embed, view=SetupView(self.conn))

        dummy = await ctx.respond("\u200B")
        await dummy.delete_original_message(delay=None)

    def build_setup_embed(self, setup_id, name):
        sign_ups, total = self.build_players_for_setup(setup_id)
        embed: discord.Embed = discord.Embed(title=f"Sign up to be part of {name}")
        for role in sign_ups:
            current = len(sign_ups[role])
            field_string = f"{role} ({current})"
            embed.add_field(
                name=field_string,
                value="\n".join(sign_ups[role])
                if len(sign_ups[role]) > 0
                else "\u200B",
            )
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text=f"total sign ups: {total} ")

        return embed

    def build_players_for_setup(self, setup_id):
        sign_ups = {
            SignUpOptions.TANK: [],
            SignUpOptions.DD: [],
            SignUpOptions.HEAL: [],
        }

        list_of_players: List[SetupPlayer] = [
            SetupPlayer(item)
            for item in select_all_players_for_setup(self.conn, setup_id)
        ]

        for index, player in enumerate(list_of_players):
            sign_ups[player.role].append(
                f"`{index + 1}` {EMOJI[player.role]} <@{player.player_id}>"
            )
        logger.info(sign_ups)
        total = len(list_of_players)

        return sign_ups, total


def setup(bot):
    bot.add_cog(SetupCog(bot))
    logger.info("Loaded Setup Cog.")
