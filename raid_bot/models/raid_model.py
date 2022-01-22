class Raid:
    def __init__(self, name, mode, description, time):
        self.name = name
        self.mode = mode
        self.description = description
        self.time = time
        self.roster = {
            "Tanks": 2,
            "DDs": 4,
            "Heals": 2
        }
        self.setup={}
        self.tentative = []
        self.absent = []

        for role in self.roster:
            self.setup[role] = []