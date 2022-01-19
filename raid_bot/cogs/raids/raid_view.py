import discord.ui
from discord.ui import Button, View
import logging

from raid_bot.models.raid_model import Raid
from raid_bot.models.raid_list_model import LIST_OF_RAIDS
from raid_bot.cogs.raids import raid_message_builder


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

VIEW_NAME = "RaidView"

class RaidView(View):

    async def handle_click_role(self, button: Button, interaction: discord.Interaction):
        user_id = interaction.user.id
        print(user_id)
        message_id = interaction.message.id
        current_raid: Raid = LIST_OF_RAIDS[message_id]
        current_raid.setup[button.custom_id].append(user_id)

        logger.info(current_raid)

        embed = raid_message_builder.build_raid_message(current_raid)

        await interaction.response.edit_message(embed=embed, view=self)



    @discord.ui.button(label="Tank", style=discord.ButtonStyle.blurple, custom_id="Tanks")
    async def tank_button(self, button, interaction):
        await self.handle_click_role(button, interaction)

    @discord.ui.button(label="DD", style=discord.ButtonStyle.red, custom_id="DDs")
    async def dd_button(self, button, interaction):
        # await interaction.response.send_message(f"You clicked {button.label}. You are {interaction.user.mention}")
        await self.handle_click_role(button, interaction)

    @discord.ui.button(label="Heal", style=discord.ButtonStyle.green, custom_id="Heals")
    async def heal_button(self, button, interaction):
       # await interaction.response.send_message(f"You clicked {button.label}. You are {interaction.user.mention}")
       await self.handle_click_role(button, interaction)

    @discord.ui.button(label="Edit", style=discord.ButtonStyle.gray, custom_id="Edit")
    async def edit_button(self, button, interaction):
        await interaction.response.send_message(f"You clicked {button.label}. You are {interaction.user.mention}")



