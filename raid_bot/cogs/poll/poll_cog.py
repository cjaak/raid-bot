from discord import slash_command, Option
from discord.ext import commands
import logging

from raid_bot.cogs.poll.poll_modal import PollModal
from raid_bot.cogs.poll.poll_view import PollView
from raid_bot.database import insert_or_replace_poll, create_table, select_one_poll
from raid_bot.models.poll_model import Poll

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PollCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = bot.conn

        create_table(self.conn, "polls")
        create_table(self.conn, "poll_options")
        create_table(self.conn, "poll_votes")

    @slash_command()
    async def poll(
        self,
        ctx,
        number_of_options: Option(
            int, "Specify number of poll options", choices=[1, 2, 3, 4]
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

        self.conn.commit()

        await ctx.interaction.response.send_modal(
            PollModal(self, number_of_options, poll_id)
        )
        await ctx.respond("Creating Poll", delete_after=0)

    async def has_poll_permission(self, poll_id, user_id):
        author_id: int = Poll(select_one_poll(self.conn, poll_id)).author_id
        if author_id == user_id:
            return True
        return False


def setup(bot):
    bot.add_cog(PollCog(bot))
    logger.info("Loaded Poll Cog.")
