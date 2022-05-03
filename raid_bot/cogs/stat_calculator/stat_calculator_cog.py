import datetime
import logging
import sys
from typing import List, Dict

import discord
from discord.commands import (
    slash_command,
    Option,
)  # Importing the decorator that makes slash commands.
from discord.ext import commands, tasks

from raid_bot.cogs.stat_calculator.stat_calculator_modal import StatCalculatorModal
from raid_bot.models.gear_models import ArmorValue, SlotDefinition, Combination

sys.path.append("../")


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TERTIARY_STATS = [
    "Accuracy",
    "Alacrity",
    "Critical Rating",
    "Shield Chance",
    "Absorption Rating",
    "None",
]


class StatCalculatorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.stats = []
        self.first_stat_target_value = 0
        self.second_stat_target_value = 0
        self.deviation = 0

        self.list_of_armor_value = []

        self.slots = SlotDefinition(10, 14, 1)

    @slash_command()
    async def calculate_tertiary_stats(
        self,
        ctx,
        first_stat: Option(str, "Choose first stat or 'None'", choices=TERTIARY_STATS),
        second_stat: Option(
            str, "Choose second stat or 'None'", choices=TERTIARY_STATS
        ),
        third_stat: Option(str, "Choose third stat or 'None'", choices=TERTIARY_STATS),
    ):
        """Calculate possible armor combinations for up to 3 stats"""
        stats, valid = self.validate_input([first_stat, second_stat, third_stat])
        if not valid:
            await ctx.respond(
                "Please select each stat only once. If you do not want to use three different stats, choose 'None' for "
                "the remaining "
            )
            return
        if not stats:
            await ctx.respond("Nothing to do for me. Every stat was set to ''None")
            return

        logger.info(stats)
        self.stats = stats

        await ctx.interaction.response.send_modal(StatCalculatorModal(self))

        # logger.info("Modal Ready")
        # first_stat_combinations = self.find_combinations(
        #     self.first_stat_target_value, self.list_of_armor_value[0]
        # )
        # if len(stats) > 1:
        #     second_stat_combinations = self.find_combinations(
        #         self.second_stat_target_value, self.list_of_armor_value[1]
        #     )
        #     complete_combinations = self.match_combinations(
        #         first_stat_combinations, second_stat_combinations
        #     )
        # else:
        #     complete_combinations = {f"{self.stats[0]}": first_stat_combinations}

    def validate_input(self, stats: List[str]):
        for stat in stats:
            if stat == "None":
                stats.remove(stat)

        if stats[-1] == "None":
            stats.pop()

        if len(stats) == len(set(stats)):
            return stats, True

        return stats, False


def setup(bot):
    bot.add_cog(StatCalculatorCog(bot))
    logger.info("Loaded Stat Calculator Cog.")
