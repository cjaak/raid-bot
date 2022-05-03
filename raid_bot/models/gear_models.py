from dataclasses import dataclass


@dataclass
class ArmorValue:
    name: str
    primary_gear_value: int
    augment_value: int
    stim_value: int

    def __init__(self, name, gear, augment, stim):
        self.name = name
        self.primary_gear_value = gear
        self.augment_value = augment
        self.stim_value = stim


@dataclass
class SlotDefinition:
    augment_slots: int
    armor_slots: int
    stim_slots: int

    def __init__(self, gear, augment, stim):
        self.armor_slots = gear
        self.augment_slots = augment
        self.stim_slots = stim


@dataclass
class Combination:
    name: str
    armor_pieces: int
    augments: int
    yellow_stim: bool
    total: int
    deviation: int

    def __init__(self, name, armor, augments, stim, total, deviation):
        self.name = name
        self.armor_pieces = armor
        self.augments = augments
        self.yellow_stim = bool(stim)
        self.total = total
        self.deviation = deviation
