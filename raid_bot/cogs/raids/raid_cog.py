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
from raid_bot.database import (
    insert_raid,
    create_table,
    get_all_raid_ids,
    get_all_raids,
    select_one_raid,
    delete_raid,
    delete_assignment,
)

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
        create_table(self.conn, "settings")

        raids = get_all_raid_ids(self.conn)
        self.raids = [raid[0] for raid in raids]
        logger.info(f"We have loaded {len(self.raids)} raids in memory.")

        self.background_task.start()

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
        setup: Option(str, "Choose a saved setup", required=False, choices=[]),
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
            setup,
        )

        self.conn.commit()

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
        expiry_time = 7200  # Delete raids after 2 hours.
        notify_time = 300  # Notify raiders 5 minutes before.
        current_time = datetime.datetime.now().timestamp()

        cutoff = current_time + 2 * notify_time
        raids = [Raid(item) for item in get_all_raids(self.conn)]
        for raid in raids:
            channel = self.bot.get_channel(raid.channel_id)
            if not channel:
                await self.cleanup_old_raid(
                    raid.raid_id, "Raid channel has been deleted."
                )
                continue
            try:
                post = await channel.fetch_message(raid.raid_id)
            except discord.NotFound:
                await self.cleanup_old_raid(raid.raid_id, "Raid post already deleted.")
            except discord.Forbidden:
                await self.cleanup_old_raid(
                    raid.raid_id,
                    "We are missing required permissions to see raid post.",
                )
            else:
                if current_time > raid.timestamp + expiry_time:
                    await self.cleanup_old_raid(
                        raid.raid_id, "Deleted expired raid post."
                    )
                    await post.delete()

        self.conn.commit()
        logger.debug("Completed raid background task.")

    async def cleanup_old_raid(self, raid_id, message):
        logger.info(message)
        guild_id = Raid(select_one_raid(self.conn, raid_id)).guild_id
        delete_raid(self.conn, raid_id)
        delete_assignment(self.conn, raid_id)
        logger.info("Deleted old raid from database.")
        await self.calendar_cog.update_calendar(guild_id, new_run=False)
        try:
            self.raids.remove(raid_id)
        except ValueError:
            logger.info("Raid already deleted from memory.")

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
