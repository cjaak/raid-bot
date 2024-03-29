from discord import slash_command, Option
from discord.ext import commands
import logging

from raid_bot.cogs.poll import poll_message_builder
from raid_bot.cogs.poll.choice_modal import ChoiceModal
from raid_bot.cogs.poll.opinion_view import OpinionView
from raid_bot.cogs.poll.poll_modal import PollModal
from raid_bot.cogs.poll.poll_view import PollView
from raid_bot.database import (
    insert_or_replace_poll,
    create_table,
    select_one_poll,
    set_question_for_poll,
)
from raid_bot.models.poll_model import Poll

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PollCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.startup())
        self.conn = bot.conn

        create_table(self.conn, "polls")
        create_table(self.conn, "poll_options")
        create_table(self.conn, "poll_votes")

    async def startup(self):
        await self.bot.wait_until_ready()
        self.bot.add_view(OpinionView(self))

    @slash_command()
    async def poll(
        self,
        ctx,
        question: Option(str, "What is the poll about?"),
        number_of_options: Option(
            int, "Specify number of poll options", choices=[1, 2, 3, 4, 5]
        ),
        multiple_selection: Option(
            bool, "Check if multiple selection should be allowed", required=False
        ),
    ):
        """Create Poll"""
        post = await ctx.send("\u200B")
        poll_id = int(post.id)

        insert_or_replace_poll(
            self.conn,
            poll_id,
            ctx.channel.id,
            ctx.guild_id,
            ctx.author.id,
            number_of_options,
            bool(multiple_selection),
        )
        set_question_for_poll(self.conn, poll_id, question)

        self.conn.commit()

        await ctx.interaction.response.send_modal(
            PollModal(self, number_of_options, poll_id)
        )
        await ctx.respond("Creating Poll", delete_after=0)

    @slash_command()
    async def opinion(self, ctx, on: Option(str, "topic")):
        post = await ctx.send("\u200B")
        poll_id = int(post.id)

        insert_or_replace_poll(
            self.conn,
            poll_id,
            ctx.channel.id,
            ctx.guild_id,
            ctx.author.id,
            0,
            False,
        )
        set_question_for_poll(self.conn, poll_id, on)

        self.conn.commit()

        embed = poll_message_builder.build_opinion_message(self.conn, poll_id)
        await post.edit(embed=embed, view=OpinionView(self))

        await ctx.respond("Creating Poll", delete_after=0)

    async def has_poll_permission(self, poll_id, user_id):
        author_id: int = Poll(select_one_poll(self.conn, poll_id)).author_id
        if author_id == user_id:
            return True
        return False

    @slash_command()
    async def random_choice(
        self,
        ctx,
        number_of_options: Option(
            int, "Specify number of poll options", choices=[1, 2, 3, 4, 5]
        ),
    ):
        await ctx.interaction.response.send_modal(ChoiceModal(number_of_options))
        await ctx.respond("Creating...", delete_after=0)


def setup(bot):
    bot.add_cog(PollCog(bot))
    logger.info("Loaded Poll Cog.")
