import logging

import discord.ui
from discord.ui import Button, View

from raid_bot.cogs.poll import poll_message_builder
from raid_bot.database import insert_or_replace_vote
from raid_bot.models.poll_emoji import OPINION_EMOJI, OpinionOptions

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class OpinionView(View):
    def __init__(self, poll_cog):
        super().__init__(timeout=None)
        self.poll_cog = poll_cog
        self.conn = poll_cog.conn

        for option in OpinionOptions:
            self.add_item(OpinionVoteButton(option))

        logger.info(f"PERSISTENT: {self.is_persistent()}")

    async def handle_click_vote(self, option, interaction: discord.Interaction):
        poll_id = interaction.message.id
        user_id = interaction.user.id

        ids = insert_or_replace_vote(self.conn, user_id, poll_id, option)

        self.conn.commit()

        embed: discord.Embed = poll_message_builder.build_opinion_message(
            self.conn, poll_id
        )

        await interaction.response.edit_message(embed=embed, view=self)


class OpinionVoteButton(Button):
    def __init__(self, option: str):
        super().__init__(emoji=OPINION_EMOJI[option], custom_id=f"opinion_{option}")

    async def callback(self, interaction: discord.Interaction):
        _, option = self.custom_id.split("_")
        await self.view.handle_click_vote(option, interaction)