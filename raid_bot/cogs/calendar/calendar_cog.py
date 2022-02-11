import sys
import logging
import datetime
from typing import List
import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from raid_bot.models.raid_list_model import Raid
from raid_bot.database import select_all_raids_by_guild_id, insert_or_replace_calendar, select_calendar

sys.path.append("../")


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CalendarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = bot.conn

    @slash_command(guild_ids=[902671732987551774])
    async def calendar(self, ctx):
        embed = self.build_calendar_embed(ctx.guild_id)
        msg = await ctx.send(embed=embed)
        ids = f"{ctx.channel.id}/{msg.id}"
        result = insert_or_replace_calendar(self.conn, ctx.guild_id, ids)
        if result:
            self.conn.commit()
            await ctx.respond(
                "The Calendar will be updated in this channel.", delete_after=20
            )
        else:
            await ctx.respond("An error occurred.", delete_after=20)
        return

    async def update_calendar(self, guild_id, new_run=True):
        calendar_id = select_calendar(self.conn, guild_id)[0]
        if not calendar_id:
            return
        ids = calendar_id.split("/")
        channel_id = ids[0]
        msg_id = ids[1]
        chn = self.bot.get_channel(channel_id)
        try:
            msg = chn.get_partial_message(msg_id)
        except AttributeError:
            logger.warning("Calendar channel not found for guild {0}.".format(guild_id))
            result = insert_or_replace_calendar(self.conn, guild_id, None)
            if result:
                self.conn.commit()
            return

        embed = self.build_calendar_embed(guild_id)
        try:
            msg.edit(embed=embed)
        except discord.Forbidden:
            pass

    def build_calendar_embed(self, guild_id: int):

        raids: List[Raid] = [
            Raid(list_item)
            for list_item in select_all_raids_by_guild_id(self.conn, guild_id)
        ]
        title: str = "Scheduled runs:"
        desc: str = "Click the link to sign up!"
        embed: discord.Embed = discord.Embed(
            title=title, description=desc, colour=discord.Colour(0x3498DB)
        )
        for raid in raids[:20]:
            timestamp = int(raid.timestamp)
            msg = "[{name} {mode}](<https://discord.com/channels/{guild}/{channel}/{msg}>)\n".format(
                guild=guild_id,
                channel=raid.channel_id,
                msg=raid.raid_id,
                name=raid.name,
                mode=raid.mode,
            )
            embed.add_field(name=f"<t:{timestamp}:F>", value=msg, inline=False)
        embed.set_footer(text="Last updated")
        embed.timestamp = datetime.datetime.utcnow()
        return embed


def setup(bot):
    bot.add_cog(CalendarCog(bot))
    logger.info("Loaded Calendar Cog.")
