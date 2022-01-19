import discord


def build_raid_message(raid):
    embed_title = f"{raid.name} {raid.mode}\n<t:{raid.time}:R>"
    embed = discord.Embed(title=embed_title, description=raid.description, colour=0x4B34EF)

    for role in raid.roster:
        current = len(raid.setup[role])
        limit = raid.roster[role]
        field_string = f"{role} {current}/{limit}"
        players = []
        for player_id in raid.setup[role]:
            players.append(f"<@{player_id}>")
        embed.add_field(name=field_string, value="\n".join(players) if len(players) > 0 else '\u200B')

    return embed
