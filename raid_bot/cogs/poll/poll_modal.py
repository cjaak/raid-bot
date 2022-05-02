import discord.ui
from discord.ext import commands
from discord.ui import Button, View, InputText
from sqlite3 import Connection
import logging

from raid_bot.cogs.poll.poll_message_builder import build_poll_message
from raid_bot.cogs.poll.poll_view import PollView
from raid_bot.cogs.time.time import Time
from raid_bot.database import (
    set_question_for_poll,
    select_one_poll,
    insert_or_replace_poll_option,
)
from raid_bot.models.poll_model import Poll
from raid_bot.models.raid_model import Raid

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MODAL_NAME = "SettingsModal"


class PollModal(discord.ui.Modal):
    def __init__(self, poll_cog, number_of_options, poll_id):
        super().__init__(title="Custom Poll")
        self.poll_cog = poll_cog
        self.conn = poll_cog.conn

        self.poll = Poll(select_one_poll(self.conn, poll_id))

        question_field = InputText(
            custom_id="poll_question", label="Question", required=True, max_length=1024
        )
        self.add_item(question_field)

        for field in range(number_of_options):
            self.add_item(
                InputText(
                    custom_id=f"field_{field}",
                    label=f"Option {field+1}",
                    required=True,
                    max_length=1024,
                )
            )

    async def callback(self, interaction: discord.Interaction):
        u_input = interaction.data["components"]
        data = {}

        for field in u_input:
            data[field["components"][0]["custom_id"]] = field["components"][0]["value"]

        set_question_for_poll(self.conn, self.poll.poll_id, data["poll_question"])
        data.pop("poll_question")

        for key, value in data.items():
            _, option_id = key.split('_')
            insert_or_replace_poll_option(self.conn, self.poll.poll_id, option_id, value)

        self.conn.commit()

        post = interaction.channel.get_partial_message(self.poll.poll_id)

        embed = build_poll_message(self.conn, self.poll.poll_id)
        await post.edit(embed=embed, view=PollView(self.poll_cog, self.poll.poll_id))

        await interaction.response.send_message("Poll was created", ephemeral=True)

        self.stop()
