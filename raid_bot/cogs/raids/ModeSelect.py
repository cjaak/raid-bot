from discord.ui import Select
from discord import Interaction
import discord
from raid_bot.database import update_raid

class ModeSelect(Select):
    def __init__(self, conn):
        options = [
            discord.SelectOption(label="1", value="SM"),
            discord.SelectOption(label="2", value="HM"),
            discord.SelectOption(label="3", value="NIM")
        ]
        self.conn = conn
        super().__init__(placeholder="Mode", options=options)

        def callback(self, interaction: Interaction):
            mode = self.value[0]
            raid_id = self.view.raid_id
            update_raid(self.conn, raid_id, "mode", mode)
            await self.view.raid_cog.update_raid()
