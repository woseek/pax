import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import deepl
from discord import option
from discord.ext import commands

from util.EmbedBuilder import EmbedBuilder
from util.Logging import log

LANGUAGES = [
    "Bulgarian",
    "Chinese",
    "Czech",
    "Danish",
    "Dutch",
    "English",
    "Estonian",
    "Finnish",
    "French",
    "German",
    "Greek",
    "Hungarian",
    "Italian",
    "Japanese",
    "Latvian",
    "Lithuanian",
    "Polish",
    "Portuguese",
    "Romanian",
    "Russian",
    "Slovak",
    "Slovenian",
    "Spanish",
    "Swedish",
]
FORMALITY_TONES = ["Formal", "Informal"]


async def translate(
    text: str,
    source_language: str,
    target_language: str,
    formality_tone: Optional[str] = None,
) -> str:
    if source_language not in LANGUAGES or target_language not in LANGUAGES:
        return "Invalid Language"

    if formality_tone is not None:
        if formality_tone not in FORMALITY_TONES:
            return "Invalid Formality Tone"

        # the DeepL API prefers that we use the lowercase version
        formality_tone = formality_tone.lower()

    # `deepl.transate` is not asynchronous, so we simply
    # pass it off to another thread and asynchronously wait for it to be completed
    with ThreadPoolExecutor() as executor:
        thread = executor.submit(
            deepl.translate,
            text=text,
            source_language=source_language,
            target_language=target_language,
            formality_tone=formality_tone,
        )

        while thread.running():
            await asyncio.sleep(0.1)

        return thread.result()


class Translation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.slash_command(name="translate", description="Translates a given text.")
    @option(
        "text",
        str,
        description="The text to translate.",
        required=True,
    )
    @option(
        "source_language",
        str,
        description="The language of the text.",
        required=True,
        choices=LANGUAGES,
    )
    @option(
        "target_language",
        str,
        description="The language to translate the text to.",
        required=True,
        choices=LANGUAGES,
    )
    @option(
        "formality_tone",
        str,
        description="The formality of the translation.",
        required=False,
        choices=FORMALITY_TONES,
    )
    async def translate(
        self,
        ctx,
        text: str,
        source_language: str,
        target_language: str,
        formality_tone: Optional[str] = None,
    ) -> None:

        try:
            translated_text = await translate(
                text, source_language, target_language, formality_tone
            )
        except Exception as e:
            embed = EmbedBuilder(
                title="Error",
                description=f"An error occurred while translating the text:\n\n{e}",
            ).build()

            await ctx.send(embed=embed)
            return

        embed = EmbedBuilder(
            title=f"Original Text ({source_language})",
            description=f"{text}",
        ).build()

        await ctx.respond(embed=embed)

        embed = EmbedBuilder(
            title=f"Translated Text ({target_language})",
            description=f"{translated_text}",
        ).build()

        await ctx.send(embed=embed)

        log(f"Translate command used by {ctx.author} in {ctx.guild}.")


def setup(bot) -> None:
    bot.add_cog(Translation(bot))
