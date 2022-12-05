import asyncio
from dataclasses import dataclass
import os
import re
import sys

import aiohttp
import discord
from dotenv import load_dotenv


@dataclass
class MedalClip:
    title: str
    url: str


def find_content_ids(text: str):
    regex = r"https://medal\.tv/games/(\S*?)/clips/([^\s?]*)/"
    matches = re.finditer(regex, text)
    return [match.group(2) for match in matches]


async def api_content(content_id: str):
    api_url = f"https://medal.tv/api/content/{content_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            data = await response.json()
            return MedalClip(data["contentTitle"], data["contentUrl"])


class Medal(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def on_message(self, message: discord.Message):
        if message.author != self.user:
            for content_id in find_content_ids(message.content):
                clip = await api_content(content_id)
                await message.channel.send(
                    f"{message.author.mention} :magic_wand: **{clip.title}**\n{clip.url}"
                )

                print(f"Fixed link for {message.author} : {message.content}")

                try:
                    await message.delete()
                except discord.errors.Forbidden:
                    print("Tried to delete message but no permissions :(")


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "get" and len(sys.argv) > 2:
            for content_id in find_content_ids(sys.argv[2]):
                return print(asyncio.run(api_content(content_id)).url)

        return print(
            "Usage:\n"
            "   Run bot:    python main.py\n"
            "   Get clip:   python main.py get https://medal.tv/..."
        )

    Medal(
        intents=discord.Intents(
            message_content=True,
            guild_messages=True,
            dm_messages=True,
        )
    ).run(os.environ["DISCORD_TOKEN"])


if __name__ == "__main__":
    load_dotenv()
    main()
