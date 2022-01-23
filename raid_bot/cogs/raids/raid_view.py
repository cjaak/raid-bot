import time
import discord.ui
from discord.ui import Button, View
import logging

from raid_bot.models.raid_model import Raid
from raid_bot.database import select_one_raid, insert_or_update_assignment
from raid_bot.models.raid_list_model import LIST_OF_RAIDS
from raid_bot.cogs.raids import raid_message_builder
from raid_bot.models.sign_up_options import SignUpOptions


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

VIEW_NAME = "RaidView"


class RaidView(View):
    def __init__(self, conn):
        super().__init__(timeout=None)
        self.conn = conn

    async def handle_click_role(self, button: Button, interaction: discord.Interaction):
        user_id = interaction.user.id
        raid_id = interaction.message.id
        # current_raid: Raid = Raid(select_one_raid(self.conn, raid_id))
        timestamp = int(time.time())
        clicked_role = button.custom_id
        insert_or_update_assignment(
            self.conn, user_id, raid_id, clicked_role, timestamp
        )
        # role_counter = len(ROLES)
        # for role in ROLES:
        #     if user_id in current_raid.setup[role]:
        #         current_raid.setup[role].remove(user_id)
        #         if role != clicked_role:
        #             current_raid.setup[clicked_role].append(user_id)
        #     else:
        #         role_counter -= 1
        #
        # if role_counter == 0:
        #     current_raid.setup[clicked_role].append(user_id)

        embed = raid_message_builder.build_raid_message(self.conn, raid_id)

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(
        label="Tank", style=discord.ButtonStyle.blurple, custom_id=SignUpOptions.TANK
    )
    async def tank_button(self, button, interaction):
        await self.handle_click_role(button, interaction)

    @discord.ui.button(label="DD", style=discord.ButtonStyle.red, custom_id=SignUpOptions.DD)
    async def dd_button(self, button, interaction):
        # await interaction.response.send_message(f"You clicked {button.label}. You are {interaction.user.mention}")
        await self.handle_click_role(button, interaction)

    @discord.ui.button(label="Heal", style=discord.ButtonStyle.green, custom_id=SignUpOptions.HEAL)
    async def heal_button(self, button, interaction):
        # await interaction.response.send_message(f"You clicked {button.label}. You are {interaction.user.mention}")
        await self.handle_click_role(button, interaction)

    @discord.ui.button(label="Edit", style=discord.ButtonStyle.gray, custom_id="edit")
    async def edit_button(self, button, interaction):
        await interaction.response.send_message(
            f"You clicked {button.label}. You are {interaction.user.mention}"
        )

    @discord.ui.button(
        label="Unavailable", style=discord.ButtonStyle.gray, custom_id=SignUpOptions.UNAVAILABLE
    )
    async def unavailable_button(self, button, interaction):
        await interaction.response.send_message(
            f"You clicked {button.label}. You are {interaction.user.mention}"
        )

    @discord.ui.button(
        label="Tentative", style=discord.ButtonStyle.gray, custom_id=SignUpOptions.TENTATIVE
    )
    async def tentative_button(self, button, interaction):
        await interaction.response.send_message(
            f"You clicked {button.label}. You are {interaction.user.mention}"
        )


ROLES = ["Tanks", "DDs", "Heals"]
