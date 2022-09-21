import sys
import logging
import datetime
import requests
from typing import List
import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from raid_bot.models.raid_list_model import Raid
from raid_bot.database import (
    select_all_raids_by_guild_id,
    insert_or_update_calendars,
    select_calendar, select_one_raid, insert_or_update_calendar_id, select_guild_events_bool,
)

sys.path.append("../")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CalendarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = bot.conn

        self.headers = {
            "Authorization": "Bot {0}".format(bot.token)
        }

    @slash_command()
    async def calendar(self, ctx, option: Option(str, "Select Calendar Format", choices=["channel", "discord", "both", "off"],required=False)):
        """Create a calendar containing all raids active on your server"""
        match option:
            case "channel":
                response = await self.setup_only_channel_calendar(ctx)
            case "discord":
                response = await self.setup_only_discord_calendar(ctx)
            case "off":
                response = await self.setup_disable_calendar(ctx)
            case _:
                response = await self.setup_both_calendar(ctx)

        await ctx.respond(response, delete_after=20)

    async def setup_only_discord_calendar(self, ctx):
        insert_or_update_calendars(self.conn, ctx.guild_id, None, True)
        return "Events will be posted as discord guild events"

    async def setup_only_channel_calendar(self, ctx):
        embed = self.build_calendar_embed(ctx.guild_id)
        msg = await ctx.send(embed=embed)
        ids = f"{ctx.channel.id}/{msg.id}"
        result = insert_or_update_calendars(self.conn, ctx.guild_id, ids, False)
        if result:
            self.conn.commit()
            return "The Calendar will be updated in this channel."
        else:
            return "An error occurred."

    async def setup_disable_calendar(self, ctx):
        insert_or_update_calendars(self.conn, ctx.guild_id, None, False)
        self.conn.commit()
        return "Events will not be posted to a calendar"

    async def setup_both_calendar(self, ctx):
        embed = self.build_calendar_embed(ctx.guild_id)
        msg = await ctx.send(embed=embed)
        ids = f"{ctx.channel.id}/{msg.id}"
        result = insert_or_update_calendars(self.conn, ctx.guild_id, ids, True)
        if result:
            self.conn.commit()
            return "The Calendar will be updated in this channel and in discord guild events."
        else:
            return "An error occurred."

    async def update_calendar(self, guild_id, new_run=True):
        calendar_id = select_calendar(self.conn, guild_id)

        if not calendar_id:
            return

        ids = calendar_id.split("/")
        channel_id = ids[0]
        msg_id = ids[1]
        chn = self.bot.get_channel(int(channel_id))
        try:
            msg = chn.get_partial_message(msg_id)
        except AttributeError:
            logger.warning("Calendar channel not found for guild {0}.".format(guild_id))
            result = insert_or_update_calendar_id(self.conn, guild_id, None)
            if result:
                self.conn.commit()
            return

        embed = self.build_calendar_embed(guild_id)
        try:
            await msg.edit(embed=embed)
        except discord.Forbidden:
            pass

        except discord.NotFound:
            logger.warning("Calendar post not found for guild {0}.".format(guild_id))
            insert_or_update_calendar_id(self.conn, guild_id, None)
            self.conn.commit()
            return
        except discord.HTTPException as e:
            logger.warning("Failed to update calendar for guild {0}.".format(guild_id))
            logger.warning(e)
            return
        if new_run:
            try:
                await chn.send(_("A new run has been posted!"), delete_after=3600)
            except discord.Forbidden:
                logger.warning("No write access to calendar channel for guild {0}.".format(guild_id))

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

    def create_guild_event(self, raid_id):
        raid: Raid = Raid(select_one_raid(self.conn, raid_id))

        res = select_guild_events_bool(self.conn, raid.guild_id)
        if not res:
            return

        metadata = {"location": f"https://discord.com/channels/{raid.guild_id}/{raid.channel_id}/{raid_id}"}
        start_time = datetime.datetime.utcfromtimestamp(raid.timestamp).isoformat() + 'Z'
        end_time = datetime.datetime.utcfromtimestamp(raid.timestamp + 7200).isoformat() + 'Z'
        event_name = f"{raid.name} {raid.mode}"

        data = {
            "entity_metadata": metadata,
            'name': event_name,
            "privacy_level": 2,
            "scheduled_start_time": start_time,
            "scheduled_end_time": end_time,
            "description": raid.description,
            "entity_type": 3
        }

        url = self.bot.api + f"guilds/{raid.guild_id}/scheduled-events"
        r = requests.post(url, headers=self.headers, json=data)
        r.raise_for_status()
        event = r.json()
        return event['id']

    def modify_guild_event(self, raid_id):
        raid: Raid = Raid(select_one_raid(self.conn, raid_id))
        if not raid.event_id:
            return

        start_time = datetime.datetime.utcfromtimestamp(raid.timestamp).isoformat() + 'Z'
        end_time = datetime.datetime.utcfromtimestamp(raid.timestamp + 7200).isoformat() + 'Z'
        data = {
            'name': f"{raid.name} {raid.mode}",
            'description': raid.description,
            'scheduled_start_time': start_time,
            'scheduled_end_time': end_time
        }
        url = self.bot.api + f"guilds/{raid.guild_id}/scheduled-events/{event_id}"
        r = requests.patch(url, headers=self.headers, json=data)
        r.raise_for_status()

    def delete_guild_event(self, raid_id):
        try:
            raid: Raid = Raid(select_one_raid(self.conn, raid_id))
        except TypeError:
            logger.info("Raid already deleted from database.")
            return
        if not raid.event_id:
            return

        url = self.bot.api + f"guilds/{raid.guild_id}/scheduled-events/{raid.event_id}"
        r = requests.delete(url, headers=self.headers)
        r.raise_for_status()


def setup(bot):
    bot.add_cog(CalendarCog(bot))
    logger.info("Loaded Calendar Cog.")
