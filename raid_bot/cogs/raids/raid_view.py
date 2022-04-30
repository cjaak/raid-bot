import time
import discord.ui
from discord.ui import Button, View
from sqlite3 import Connection
import logging

from raid_bot.cogs.raids.settings_modal import SettingsModal
from raid_bot.models.raid_model import Raid
from raid_bot.database import select_one_raid, insert_or_update_assignment
from raid_bot.cogs.raids import raid_message_builder
from raid_bot.models.sign_up_options import SignUpOptions, EMOJI


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

VIEW_NAME = "RaidView"


class RaidView(View):
    def __init__(self, raid_cog):
        super().__init__(timeout=None)
        self.raid_cog = raid_cog
        self.conn = raid_cog.conn
        for option in SignUpOptions:
            self.add_item(SignUpButton(option))

        self.add_item(SettingsButton())

    async def handle_click_role(self, role: str, interaction: discord.Interaction):
        user_id: int = interaction.user.id
        raid_id: int = interaction.message.id
        timestamp = int(time.time())
        insert_or_update_assignment(self.conn, user_id, raid_id, role, timestamp)
        self.conn.commit()

        embed: discord.Embed = raid_message_builder.build_raid_message(
            self.conn, raid_id
        )

        await interaction.response.edit_message(embed=embed, view=self)

    async def settings(
        self, interaction: discord.Interaction
    ):

        if not interaction.message.author:
            perm_msg = "You do not have permission to change the raid settings."
            await interaction.response.send_message(perm_msg, ephemeral=True)
            return
        msg = (
            "Please select the setting to update or delete the raid.\n"
            "(This selection message is ephemeral and will cease to work after 60s without interaction.)"
        )
        modal = SettingsModal(self.raid_cog, interaction.message.id)
        await interaction.response.send_modal(modal)


class SignUpButton(Button):
    def __init__(self, option: str):
        super().__init__(emoji=EMOJI[option], custom_id=f"raid_{option}")

    async def callback(self, interaction: discord.Interaction):
        _, role = self.custom_id.split("_")
        await self.view.handle_click_role(role, interaction)


class SettingsButton(Button):
    def __init__(self):
        super().__init__(
            emoji="\U0001F6E0\uFE0F",
            style=discord.ButtonStyle.blurple,
            custom_id="raid_view:settings",
        )

    async def callback(self, interaction: discord.Interaction):
        await self.view.settings(interaction)
