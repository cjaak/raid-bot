import logging
import sys

import discord
from discord.commands import (
    slash_command,
    Option,
)  # Importing the decorator that makes slash commands.
from discord.ext import commands

from raid_bot.cogs.setup.setup_message_builder import build_setup_embed
from raid_bot.cogs.setup.setup_view import SetupView

sys.path.append("../")

from raid_bot.database import (
    insert_or_replace_setup,
    create_table,
    get_all_setup_ids,
    delete_setup,
    delete_setupplayers,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.startup())
        self.conn = self.bot.conn

        create_table(self.conn, "setup")
        create_table(self.conn, "setup_players")
        setups = get_all_setup_ids(self.conn)
        self.setups = [item[0] for item in setups]
        logger.info(f"We have loaded {len(self.setups)} setups in memory.")

    @slash_command()
    async def setup(self, ctx, name: Option(str, "Name this setup.")):
        """Create a setup for your server"""

        post = await ctx.send("\u200B")
        setup_id = int(post.id)

        processed_name = name.lower().strip()

        insert_or_replace_setup(
            self.conn, setup_id, ctx.guild_id, ctx.channel.id, processed_name
        )
        self.conn.commit()

        embed: discord.Embed = build_setup_embed(self.conn, setup_id)

        await post.edit(embed=embed, view=SetupView(self.conn))

        dummy = await ctx.respond("\u200B")
        await dummy.delete_original_message(delay=None)

    async def startup(self):
        await self.bot.wait_until_ready()
        self.bot.add_view(SetupView(self.conn))

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        setup_id = payload.message_id
        if setup_id in self.setups:
            # Handle clean up on bot side
            await self.cleanup_old_setup(setup_id, "Setup manually deleted.")
            self.conn.commit()

    async def cleanup_old_setup(self, setup_id, message):
        logger.info(message)
        delete_setup(self.conn, setup_id)
        delete_setupplayers(self.conn, setup_id)
        logger.info("Deleted old setup from database.")
        try:
            self.setups.remove(setup_id)
        except ValueError:
            logger.info("Setup already deleted from memory.")


def setup(bot):
    bot.add_cog(SetupCog(bot))
    logger.info("Loaded Setup Cog.")
