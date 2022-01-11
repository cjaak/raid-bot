import discord.ui
from discord.ui import Button, View


from raid_bot.models.raid_model import Raid
from raid_bot.models.raid_list_model import LIST_OF_RAIDS

VIEW_NAME = "RaidView"

class RaidView(View):

    async def handle_click_role(self, button: Button, interaction: discord.Interaction):
        user_id = interaction.user.id
        message_id = interaction.message.id
        current_raid: Raid = LIST_OF_RAIDS[message_id]
        current_raid.setup[button.custom_id].append(user_id)

        embed = self.build_raid_message(current_raid)

        await interaction.response.edit_message(embed=embed, view=self)



    @discord.ui.button(label="Tank", style=discord.ButtonStyle.blurple, custom_id="Tanks")
    async def tank_button(self, button, interaction):
        await self.handle_click_role(button, interaction)

    @discord.ui.button(label="DD", style=discord.ButtonStyle.red, custom_id="DDs")
    async def dd_button(self, button, interaction):
        await interaction.response.send_message(f"You clicked {button.label}. You are {interaction.user.mention}")

    @discord.ui.button(label="Heal", style=discord.ButtonStyle.green, custom_id="Heals")
    async def heal_button(self, button, interaction):
        await interaction.response.send_message(f"You clicked {button.label}. You are {interaction.user.mention}")


    def build_raid_message(self, raid):
        embed_title = f"{raid.name} {raid.mode}\n<t:{raid.time}:F>"
        embed = discord.Embed(title=embed_title, description=raid.description, colour=0x4B34EF)

        for role in raid.roster:
            current = len(raid.setup[role])
            limit = raid.roster[role]
            field_string = f"{role} {current}/{limit}"
            embed.add_field(name=field_string, value='\u200b')
        return embed