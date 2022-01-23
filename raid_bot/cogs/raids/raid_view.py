import time
import discord.ui
from discord.ui import Button, View
import logging

from raid_bot.models.raid_model import Raid
from raid_bot.database import select_one_raid, insert_or_update_assignment
from raid_bot.models.raid_list_model import LIST_OF_RAIDS
from raid_bot.cogs.raids import raid_message_builder
from raid_bot.models.sign_up_options import SignUpOptions, EMOJI


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

VIEW_NAME = "RaidView"


class RaidView(View):
    def __init__(self, conn):
        super().__init__(timeout=None)
        self.conn = conn
        for option in SignUpOptions:
            self.add_item(SignUpButton(option))

    async def handle_click_role(self, role: str, interaction: discord.Interaction):
        user_id = interaction.user.id
        raid_id = interaction.message.id
        timestamp = int(time.time())
        insert_or_update_assignment(
            self.conn, user_id, raid_id, role, timestamp
        )

        embed = raid_message_builder.build_raid_message(self.conn, raid_id)

        await interaction.response.edit_message(embed=embed, view=self)

    # @discord.ui.button(
    #     label="Tank", style=discord.ButtonStyle.blurple, custom_id=SignUpOptions.TANK
    # )
    # async def tank_button(self, button, interaction):
    #     await self.handle_click_role(button, interaction)
    #
    # @discord.ui.button(label="DD", style=discord.ButtonStyle.red, custom_id=SignUpOptions.DD)
    # async def dd_button(self, button, interaction):
    #     # await interaction.response.send_message(f"You clicked {button.label}. You are {interaction.user.mention}")
    #     await self.handle_click_role(button, interaction)
    #
    # @discord.ui.button(label="Heal", style=discord.ButtonStyle.green, custom_id=SignUpOptions.HEAL)
    # async def heal_button(self, button, interaction):
    #     # await interaction.response.send_message(f"You clicked {button.label}. You are {interaction.user.mention}")
    #     await self.handle_click_role(button, interaction)
    #
    # @discord.ui.button(label="Edit", style=discord.ButtonStyle.gray, custom_id="edit")
    # async def edit_button(self, button, interaction):
    #     await interaction.response.send_message(
    #         f"You clicked {button.label}. You are {interaction.user.mention}"
    #     )
    #
    # @discord.ui.button(
    #     label="Unavailable", style=discord.ButtonStyle.gray, custom_id=SignUpOptions.UNAVAILABLE
    # )
    # async def unavailable_button(self, button, interaction):
    #     await interaction.response.send_message(
    #         f"You clicked {button.label}. You are {interaction.user.mention}"
    #     )
    #
    # @discord.ui.button(
    #     label="Tentative", style=discord.ButtonStyle.gray, custom_id=SignUpOptions.TENTATIVE
    # )
    # async def tentative_button(self, button, interaction):
    #     await interaction.response.send_message(
    #         f"You clicked {button.label}. You are {interaction.user.mention}"
    #     )


class SignUpButton(Button):
    def __init__(self, option):
        super().__init__(emoji=EMOJI[option], custom_id=option)

    async def callback(self, interaction: discord.Interaction):
        role = self.custom_id
        await self.view.handle_click_role(role, interaction)