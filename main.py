import asyncio
import json
import os
import re
import sys

import aiohttp
import discord
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()


async def get_medal_clip(clip_path: str) -> dict | None:
    original_url = f"https://medal.tv/games/{clip_path}"
    async with aiohttp.ClientSession() as session:
        # get page source to extract __NEXT_DATA__
        async with session.get(original_url) as response:
            source = await response.text()
            next_data_script = BeautifulSoup(source, "lxml").find(
                "script", {"id": "__NEXT_DATA__"}
            )
            if next_data_script is None:
                return None

        next_data = json.loads(next_data_script.text)

        # get the build id from next_data
        build_id: str = next_data["buildId"]

        # get clip data from newest build
        api_path = f"https://medal.tv/_next/data/{build_id}/en/games/{clip_path}.json"
        async with session.get(api_path) as response:
            return await response.json()


class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def on_message(self, message: discord.Message):
        # we do not want the bot to reply to itself
        if message.author == self.user:
            return

        regex = r"https://medal\.tv/games/([^\s?]*)"
        matches = re.finditer(regex, message.content)
        for match in matches:
            data = await get_medal_clip(match.group(1))
            if data is None:
                return print(f"Could not find next data from {match.group(1)}")

            content_url = data["pageProps"]["clip"]["contentUrl"]
            content_title = data["pageProps"]["clip"]["contentTitle"]

            await message.reply(
                f":magic_wand: **{content_title}** {content_url}", mention_author=True
            )

            print(f"Fixed link for {message.author} : {message.content}")

            try:
                await asyncio.sleep(1)
                await message.edit(suppress=True)
            except discord.errors.Forbidden:
                print("Tried to suppress message but no permissions :(")


if len(sys.argv) > 1 and sys.argv[1] == "get":
    try:
        clip = sys.argv[2]
        asyncio.run(get_medal_clip(clip))
    except IndexError:
        print(
            "Usage:\n"
            "   Run bot:    python main.py\n"
            "   Get clip:   python main.py get https://medal.tv/..."
        )
else:
    intents = discord.Intents.default()
    intents.message_content = True

    client = MyClient(intents=intents)
    client.run(os.environ["DISCORD_TOKEN"])
