import time
import discord.ui
from discord.ui import Button, View
from sqlite3 import Connection
import logging

from raid_bot.models.setup_player_model import SetupPlayer
from raid_bot.database import insert_or_replace_setup, select_one_setup
from raid_bot.cogs.raids import raid_message_builder
from raid_bot.models.sign_up_options import SignUpOptions, EMOJI


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

VIEW_NAME = "SetupView"


class SetupView(View):
    def __init__(self, conn: Connection):
        super().__init__(timeout=None)
        self.conn = conn

    async def handle_click_role(self, role: str, interaction: discord.Interaction):
        user_id: int = interaction.user.id
        raid_id: int = interaction.message.id
        timestamp = int(time.time())
        insert_or_replace_setup(self.conn, ctx.guild_id)
        self.conn.commit()

        embed: discord.Embed = raid_message_builder.build_raid_message(
            self.conn, raid_id
        )

        await interaction.response.edit_message(embed=embed, view=self)