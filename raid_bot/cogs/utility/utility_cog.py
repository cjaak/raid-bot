from discord.ext import commands
import sys
import discord
import logging
from discord.commands import slash_command

sys.path.append("../")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = bot.conn
        self.raid_cog = bot.get_cog("RaidCog")
        self.setup_cog = bot.get_cog("SetupCog")

    @slash_command()
    async def clear_channel(self, ctx):
        """Deletes all messages in this channel"""
        if not ctx.user.guild_permissions.administrator:
            await ctx.respond("You are not allowed to do that")
            return
        messages = await ctx.channel.history().flatten()
        await ctx.respond(f"Deleting {len(messages)} Messages", delete_after=5)
        logger.info("deleting messages")
        for message in messages:
            await message.delete()
            if message.id in self.raid_cog.raids:
                await self.raid_cog.cleanup_old_raid(
                    message.id, "Deleted by clear_channel command"
                )
            elif message.id in self.setup_cog.setups:
                await self.setup_cog.cleanup_old_setup(
                    message.id, "Deleted by clear_channel command"
                )


def setup(bot):
    bot.add_cog(UtilityCog(bot))
    logger.info("Loaded Utility Cog.")
