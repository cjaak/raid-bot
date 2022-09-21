import discord.ui
import requests
from discord.ext import commands
from discord.ui import Button, View
from sqlite3 import Connection
import logging

from raid_bot.cogs.time.time import Time
from raid_bot.database import select_one_raid, update_raid
from raid_bot.models.raid_model import Raid

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MODAL_NAME = "SettingsModal"


class SettingsModal(discord.ui.Modal):
    def __init__(self, raid_cog, raid_id):
        super().__init__(title="Raid Settings")
        self.raid_cog = raid_cog
        self.calendar_cog = raid_cog.bot.get_cog("CalendarCog")
        self.raid_id = raid_id
        self.conn = raid_cog.conn
        try:
            self.raid = Raid(select_one_raid(self.conn, raid_id))
        except TypeError:
            logger.info("The raid has been deleted during editing.")
            return
        name_field = discord.ui.InputText(
            custom_id="name", label="Name", value=self.raid.name, max_length=256
        )
        mode_field = discord.ui.InputText(
            custom_id="mode",
            label="Mode",
            required=False,
            value=self.raid.mode,
            max_length=8,
        )
        description_field = discord.ui.InputText(
            custom_id="description",
            label="Description",
            required=False,
            value=self.raid.description,
            max_length=1024,
        )
        time_field = discord.ui.InputText(
            custom_id="time",
            label="Time",
            required=False,
            placeholder="Leave blank to keep the existing time.",
            max_length=64,
        )
        delete_field = discord.ui.InputText(
            custom_id="delete",
            label="Delete",
            required=False,
            placeholder="Type 'delete' here to delete the raid.",
            max_length=8,
        )
        self.add_item(name_field)
        self.add_item(mode_field)
        self.add_item(description_field)
        self.add_item(time_field)
        self.add_item(delete_field)

    async def callback(self, interaction: discord.Interaction):
        data = interaction.data["components"]
        settings = {}

        for field in data:
            settings[field["components"][0]["custom_id"]] = field["components"][0][
                "value"
            ]

        logger.info(settings)

        if settings["delete"].lower() == "delete":
            await self.delete_raid(interaction)
            self.stop()
            return

        logger.info("Not exited after delete")

        settings.pop("delete")

        resp_msg = "The raid settings have been successfully updated!"

        if settings["time"]:
            try:
                timestamp = Time().converter(self.raid_cog.bot, settings["time"])
            except commands.BadArgument:
                resp_msg = f"Failed to parse time argument: {settings['time']}"
                settings.pop("time")
            else:
                settings["time"] = timestamp
        else:
            settings.pop("time")

        for key, value in settings.items():
            update_raid(self.conn, self.raid.raid_id, key, value)

        self.conn.commit()

        await interaction.response.send_message(resp_msg, ephemeral=True)

        await self.raid_cog.update_raid_post(self.raid_id, interaction.channel)
        await self.calendar_cog.update_calendar(interaction.guild.id, new_run=False)

        try:
            self.calendar_cog.modify_guild_event(self.raid_id)
        except requests.HTTPError as e:
            logger.warning(e.response.text)

        self.stop()

    async def delete_raid(self, interaction: discord.Interaction):
        # await interaction.response.defer()

        # Delete the guild event
        try:
            self.calendar_cog.delete_guild_event(self.raid_id)
        except requests.HTTPError as e:
            logger.warning(e.response.text)

        await self.raid_cog.cleanup_old_raid(self.raid_id, "Raid deleted via button.")
        post = interaction.channel.get_partial_message(self.raid_id)
        try:
            await post.delete()
        except discord.NotFound:
            pass

        await interaction.response.send_message("Raid was deleted", ephemeral=True)
