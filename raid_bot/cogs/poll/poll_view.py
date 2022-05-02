import logging
import time

import discord.ui
from discord.ui import Button, View

from raid_bot.cogs.poll import poll_message_builder
from raid_bot.database import (
    insert_or_replace_vote,
    select_one_poll,
    delete_poll_votes_options,
    set_or_add_vote,
)
from raid_bot.models.poll_emoji import POLL_EMOJI
from raid_bot.models.poll_model import Poll

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

VIEW_NAME = "PollView"


class PollView(View):
    def __init__(self, poll_cog, poll_id):
        super().__init__(timeout=None)
        self.poll_cog = poll_cog
        self.conn = poll_cog.conn
        self.poll = Poll(select_one_poll(self.conn, poll_id))

        for i in range(int(self.poll.number_of_options)):
            self.add_item(VoteButton(i))

        self.add_item(EndPollButton())

    async def handle_click_vote(self, option: int, interaction: discord.Interaction):
        user_id: int = interaction.user.id
        poll_id: int = interaction.message.id

        ids = []
        if not self.poll.multiple_selection:
            ids = insert_or_replace_vote(self.conn, user_id, poll_id, option)
        else:
            ids = set_or_add_vote(self.conn, user_id, poll_id, option)

        self.conn.commit()

        embed: discord.Embed = poll_message_builder.build_poll_message(
            self.conn, poll_id
        )

        logger.info(ids)

        msg = self.create_vote_msg(ids)

        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(msg, ephemeral=True, delete_after=3)

    async def handle_end_poll(self, interaction: discord.Interaction):
        poll_id = interaction.message.id
        user_id = interaction.user.id
        if not await self.poll_cog.has_poll_permission(poll_id, user_id):
            await interaction.response.send_message(
                "You do not have permission to do that"
            )
            return

        embed = poll_message_builder.build_poll_result_message(self.conn, poll_id)

        await interaction.response.send_message(embed=embed)
        delete_poll_votes_options(self.conn, poll_id)

        post = interaction.channel.get_partial_message(poll_id)
        try:
            await post.delete()
        except discord.NotFound:
            pass

    def create_vote_msg(self, options):
        if not options or options[0] == "":
            return f"You are currently not voting"
        msg = f"You selected "
        for i in options:
            if i:
                msg += f"{POLL_EMOJI[int(i)]} "
        return msg


class VoteButton(Button):
    def __init__(self, option: int):
        super().__init__(emoji=POLL_EMOJI[option], custom_id=f"poll_{option}")

    async def callback(self, interaction: discord.Interaction):
        _, option = self.custom_id.split("_")
        await self.view.handle_click_vote(int(option), interaction)


class EndPollButton(Button):
    def __init__(self):
        super().__init__(
            label="END POLL", custom_id=f"poll_end", style=discord.ButtonStyle.green
        )

    async def callback(self, interaction: discord.Interaction):
        await self.view.handle_end_poll(interaction)
