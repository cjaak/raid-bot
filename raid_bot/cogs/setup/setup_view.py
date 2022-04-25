import time
import discord.ui
from discord.ui import Button, View
from sqlite3 import Connection
import logging

from raid_bot.models.setup_model import Setup
from raid_bot.database import insert_or_replace_setupplayer
from raid_bot.cogs.setup import setup_message_builder
from raid_bot.models.sign_up_options import SignUpOptions, EMOJI


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

VIEW_NAME = "SetupView"

class SetupView(View):
    def __init__(self, conn: Connection):
        super().__init__(timeout=None)
        self.conn = conn
        for option in [SignUpOptions.TANK, SignUpOptions.DD, SignUpOptions.HEAL]:
            self.add_item(SignUpButton(option))

    async def handle_click_role(self, role: str, interaction: discord.Interaction):
        user_id: int = interaction.user.id
        setup_id: int = interaction.message.id
        insert_or_replace_setupplayer(self.conn, user_id, setup_id, role)
        self.conn.commit()

        embed: discord.Embed = setup_message_builder.build_setup_embed(
            self.conn, setup_id
        )

        await interaction.response.edit_message(embed=embed, view=self)



class SignUpButton(Button):
    def __init__(self, option: str):
        super().__init__(emoji=EMOJI[option], custom_id=option)

    async def callback(self, interaction: discord.Interaction):
        role: str = self.custom_id
        await self.view.handle_click_role(role, interaction)
