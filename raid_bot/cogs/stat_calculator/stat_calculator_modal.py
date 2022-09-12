import json
import pprint
from typing import List, Dict

import discord.ui
from discord.ui import Button, View, InputText
import logging

from raid_bot.models.gear_models import ArmorValue, SlotDefinition, Combination


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MODAL_NAME = "StatCalculatorModal"


class StatCalculatorModal(discord.ui.Modal):
    def __init__(self, stat_calculator_cog):
        super().__init__(title="Stat Calculator")
        self.stat_calculator_cog = stat_calculator_cog
        self.stats = stat_calculator_cog.stats

        self.first_stat_target_value = 0
        self.second_stat_target_value = 0
        self.deviation = 0

        self.list_of_armor_value = []

        self.slots = SlotDefinition(10, 14, 1)

        number = 2 if len(self.stats) == 3 else len(self.stats)

        for value in range(number):
            self.add_item(
                InputText(
                    custom_id=f"value_{value+1}",
                    label=f"TARGET VALUE FOR {self.stats[value]}",
                    required=True,
                    max_length=5,
                    value=str(2694 if value == 0 else 2054),
                )
            )

        self.add_item(
            InputText(
                custom_id=f"deviation",
                label=f"LARGEST DEVIATION ABOVE THE TARGET VALUE",
                required=True,
                max_length=5,
                value=str(30),
            )
        )

        self.add_item(
            InputText(
                custom_id=f"augment_value",
                label="TERTIARY STATS OF AUGMENTS",
                required=True,
                max_length=3,
                value=str(108),
            )
        )

        self.add_item(
            InputText(
                custom_id=f"armor_value",
                label="TERTIARY STATS OF PRIMARY GEAR",
                required=True,
                max_length=3,
                value=str(554),
            )
        )

    async def callback(self, interaction: discord.Interaction):
        u_input = interaction.data["components"]
        data = {}

        for field in u_input:
            data[field["components"][0]["custom_id"]] = field["components"][0]["value"]

        configuration = {}
        self.first_stat_target_value = int(data["value_1"])
        configuration[f"TARGET_VALUE_{self.stats[0].upper()}"] = data["value_1"]
        if "value_2" in data:
            self.second_stat_target_value = int(data["value_2"])
            configuration[f"TARGET_VALUE_{self.stats[1].upper()}"] = data["value_2"]

        deviation = int(data["deviation"])
        self.deviation = deviation

        augment_value = int(data["augment_value"])
        armor_value = int(data["armor_value"])

        for stat in self.stats:
            stim = 0
            if stat == "Critical Rating":
                stim = 109
            elif stat == "Accuracy":
                stim = 264
            self.list_of_armor_value.append(
                ArmorValue(stat, armor_value, augment_value, stim)
            )

        configuration[f"ARMOR_VALUE"] = armor_value
        configuration[f"AUGMENT_VALUE"] = augment_value
        configuration[f"MAX_DEVIATION"] = deviation

        pretty_dict_input = pprint.pformat(configuration)
        await interaction.response.send_message(f"```{pretty_dict_input}```")

        first_stat_combinations = self.find_combinations(
            self.first_stat_target_value,
            self.list_of_armor_value[0],
        )

        if len(self.stats) > 1:
            second_stat_combinations = self.find_combinations(
                self.second_stat_target_value,
                self.list_of_armor_value[1],
            )
            complete_combinations = self.match_combinations(
                first_stat_combinations, second_stat_combinations
            )
        else:
            complete_combinations = self.fill_rest_combination(first_stat_combinations)

        pretty_dict_str = pprint.pformat(complete_combinations)
        await interaction.followup.send(f"``` {pretty_dict_str}```")

        self.stop()

    def find_combinations(self, target_value: int, armor_value: ArmorValue):
        combinations: List[Combination] = []
        for armor in range(self.slots.armor_slots + 1):
            for augment in range(self.slots.augment_slots + 1):
                for stim in range(self.slots.stim_slots + 1):
                    value = (
                        armor * armor_value.primary_gear_value
                        + augment * armor_value.augment_value
                        + stim * armor_value.stim_value
                    )
                    difference = value - target_value
                    if difference < self.deviation and value > target_value:
                        combinations.append(
                            Combination(
                                armor_value.name,
                                armor,
                                augment,
                                stim,
                                value,
                                difference,
                            )
                        )

        return combinations

    def match_combinations(
        self,
        combinations_value_1: List[Combination],
        combinations_value_2: List[Combination],
    ):
        complete_combinations = []
        rest = "Rest" if len(self.stats) <= 2 else self.stats[2]
        for v1 in combinations_value_1:
            for v2 in combinations_value_2:
                if (
                    v1.augments + v2.augments <= self.slots.augment_slots
                    and v1.armor_pieces + v2.armor_pieces <= self.slots.armor_slots
                    and v1.yellow_stim == v2.yellow_stim
                ):
                    rest_armor = self.slots.armor_slots - (
                        v1.armor_pieces + v2.armor_pieces
                    )
                    rest_augments = self.slots.augment_slots - (
                        v1.augments + v2.augments
                    )
                    rest_total = (
                        rest_armor * self.list_of_armor_value[0].primary_gear_value
                        + rest_augments * self.list_of_armor_value[0].augment_value
                    )
                    stim = 0
                    if rest == "Critical Rating":
                        rest_total += 82
                        stim = 109
                    rest_total += stim if v1.yellow_stim else rest_total
                    complete_combinations.append(
                        {
                            f"{v1.name}": v1,
                            f"{v2.name}": v2,
                            f"{rest}": Combination(
                                rest,
                                rest_armor,
                                rest_augments,
                                v1.yellow_stim,
                                rest_total,
                                0,
                            ),
                        }
                    )
        return complete_combinations

    def fill_rest_combination(self, combinations: List[Combination]):
        complete_combinations = []
        for combo in combinations:
            rest_armor = self.slots.armor_slots - combo.armor_pieces
            rest_augments = self.slots.augment_slots - combo.augments
            rest_total = (
                rest_armor * self.list_of_armor_value[0].primary_gear_value
                + rest_augments * self.list_of_armor_value[0].augment_value
            )
            complete_combinations.append(
                {
                    f"{combo.name}": combo,
                    f"Rest": Combination(
                        "Rest",
                        rest_armor,
                        rest_augments,
                        combo.yellow_stim,
                        rest_total,
                        0,
                    ),
                }
            )
            return complete_combinations
