import random

from discord import Interaction
from discord.ui import Modal, InputText


class ChoiceModal(Modal):
    def __init__(self, number_of_options):
        super().__init__(title="Random Choice")

        for item in range(number_of_options):
            self.add_item(
                InputText(
                    custom_id=f"choice_{item}",
                    label=f"Option {item +1}",
                    required=True,
                )
            )

    async def callback(self, interaction: Interaction):
        u_input = interaction.data["components"]
        data = []

        for field in u_input:
            data.append(field["components"][0]["value"])

        choice = random.choice(data)

        await interaction.response.send_message(f"I have chosen `{choice}` for you.")

