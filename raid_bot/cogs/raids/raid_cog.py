import requests as requests
from discord import Interaction
from discord.ext import commands, tasks
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
from raid_bot.database import insert_raid, create_table, get_all_raid_ids

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

        raids = get_all_raid_ids(self.conn)
        self.raids = [raid[0] for raid in raids]
        logger.info(f"We have loaded {len(self.raids)} raids in memory.")


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

        self.raids.append(raid_id)

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

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        raid_id = payload.message_id
        if raid_id in self.raids:
            # Delete the guild event
            try:
                self.calendar_cog.delete_guild_event(raid_id)
            except requests.HTTPError as e:
                logger.warning(e.response.text)
            # Handle clean up on bot side
            await self.cleanup_old_raid(raid_id, "Raid manually deleted.")
            self.conn.commit()

    @tasks.loop(seconds=300)
    async def background_task(self):
        bot = self.bot
        expiry_time = 7200  # Delete raids after 2 hours.
        notify_time = 300  # Notify raiders 5 minutes before.
        current_time = datetime.datetime.now().timestamp()

        cutoff = current_time + 2 * notify_time
        # raids = select_le(self.conn, 'Raids', ['raid_id', 'channel_id', 'time', 'roster'], ['time'], [cutoff])
        # for raid in raids:
        #     raid_id = int(raid[0])
        #     channel_id = int(raid[1])
        #     timestamp = int(raid[2])
        #     roster = int(raid[3])
        #     channel = bot.get_channel(channel_id)
        #     if not channel:
        #         await self.cleanup_old_raid(raid_id, "Raid channel has been deleted.")
        #         continue
        #     try:
        #         post = await channel.fetch_message(raid_id)
        #     except discord.NotFound:
        #         await self.cleanup_old_raid(raid_id, "Raid post already deleted.")
        #     except discord.Forbidden:
        #         await self.cleanup_old_raid(raid_id, "We are missing required permissions to see raid post.")
        #     else:
        #         if current_time > timestamp + expiry_time:
        #             await self.cleanup_old_raid(raid_id, "Deleted expired raid post.")
        #             await post.delete()
        #         elif current_time < timestamp - notify_time:
        #             raid_start_msg = _("Gondor calls for aid! Will you answer the call")
        #             if roster:
        #                 players = select(self.conn, 'Assignment', ['player_id'], ['raid_id'], [raid_id])
        #                 player_msg = " ".join(["<@{0}>".format(player[0]) for player in players if player[0]])
        #                 raid_start_msg = " ".join([raid_start_msg, player_msg])
        #             raid_start_msg = raid_start_msg + _("? We are forming for the raid now.")
        #             try:
        #                 await channel.send(raid_start_msg, delete_after=notify_time * 2)
        #             except discord.Forbidden:
        #                 self.logger.warning(
        #                     "Missing permissions to send raid notification to channel {0}".format(channel.id))
        #
        # self.conn.commit()
        # logger.debug("Completed raid background task.")

    @background_task.before_loop
    async def before_background_task(self):
        await self.bot.wait_until_ready()

    @background_task.error
    async def handle_error(self, exception):
        logger.error("Raid background task failed.")
        logger.error(exception, exc_info=True)


def setup(bot):
    bot.add_cog(RaidCog(bot))
    logger.info("Loaded Raid Cog.")
