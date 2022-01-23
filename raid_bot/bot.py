from datetime import datetime
from typing import List
import discord
from discord.ext import commands
from dotenv import load_dotenv
import gettext
import json
import locale
import logging
import os
import re

from database import create_connection


class Bot(commands.Bot):
    def __init__(self):
        self.launch_time = datetime.utcnow()

        logfile = "raid_bot.log"
        logging.basicConfig(
            filename=logfile,
            level=logging.WARNING,
            format="%(asctime)s %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        self.logger = logger
        load_dotenv()
        try:
            self.token = os.getenv("BOT_TOKEN")
        except KeyError:
            logging.critical("Please supply a discord bot token.")
            raise SystemExit

        with open('data/config.json', 'r') as f:
            config = json.load(f)

        self.server_tz = config['SERVER_TZ']

        conn = create_connection('raid_db')
        if conn:
            self.logger.info("Bot connected to raid database.")
        self.conn = conn

        intents = discord.Intents.none()
        intents.guilds = True
        intents.messages = True

        super().__init__(
            command_prefix="!",
            case_insensitive=True,
            intents=intents,
            activity=discord.Game(name="Hello there!"),
        )

        def globally_block_dms(ctx):
            if ctx.guild is None:
                raise commands.NoPrivateMessage("No dm allowed!")
            else:
                return True

        super().add_check(globally_block_dms)

    async def on_ready(self):
        self.logger.info("We have logged in as {0}.".format(self.user))
        if not self.guilds:
            self.logger.error("The bot is not in any guilds. Shutting down.")
            await self.close()
            return
        for guild in self.guilds:
            self.logger.info("Welcome to {0}.".format(guild))

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(_("Please use this command in a server."))
        else:
            if not isinstance(error, commands.CommandNotFound):
                self.logger.warning("Error for command: " + ctx.message.content)
                self.logger.warning(error)
            try:
                await ctx.send(error, delete_after=10)
            except discord.Forbidden:
                self.logger.warning(
                    "Missing Send messages permission for channel {0}".format(
                        ctx.channel.id
                    )
                )

    # async def on_command_completion(self, ctx):
    #     timestamp = int(datetime.now().timestamp())
    #     upsert(self.conn, 'Settings', ['last_command'], [timestamp], ['guild_id'], [ctx.guild.id])
    #     increment(self.conn, 'Settings', 'command_count', ['guild_id'], [ctx.guild.id])
    #     self.conn.commit()
