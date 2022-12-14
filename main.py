import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
discord_intents = discord.Intents.default()
discord_intents.message_content = True
bot = commands.Bot(command_prefix="g.", intents=discord_intents)


def load() -> None:
    cogs = [
        "Alerts",
        "DeepL",
        "Information",
        "MerriamWebster",
        "Misc",
        # "Moderation",
        "PubChem",
        "Rules",
        "Surveys",
        "Wikipedia",
    ]
    for cog in cogs:
        bot.load_extension(f"cogs.{cog}")


if __name__ == "__main__":
    load()
    bot.run(TOKEN)
