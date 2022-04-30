from discord.ui import Select
from discord import Interaction
import discord
from raid_bot.database import update_raid


class RaidSelect(Select):
    def __init__(self, conn):
        options = [discord.SelectOption(label="foo", value="bar")]
        self.conn = conn
        super().__init__(placeholder="Raid", options=options)

    def callback(self, interaction: Interaction):
        name = self.value[0]
        raid_id = self.view.raid_id
        update_raid(self.conn, raid_id, "name", name)
        await self.view.raid_cog.update_raid()
