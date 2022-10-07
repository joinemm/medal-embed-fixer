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


async def get_medal_clip(clip_path: str) -> dict:
    original_url = f"https://medal.tv/games/{clip_path}"
    async with aiohttp.ClientSession() as session:
        # get page source to extract __NEXT_DATA__
        async with session.get(original_url) as response:
            source = await response.text()
            next_data = json.loads(
                BeautifulSoup(source, "lxml").find("script", {"id": "__NEXT_DATA__"}).text
            )

        # get the build id from next_data
        build_id = next_data["buildId"]

        # get clip data from newest build
        async with session.get(
            f"https://medal.tv/_next/data/{build_id}/en/games/{clip_path}.json"
        ) as response:
            return await response.json()


class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_message(self, message: discord.Message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        regex = r"https://medal\.tv/games/([^\s?]*)"
        matches = re.finditer(regex, message.content)
        for match in matches:
            data = await get_medal_clip(match.group(1))

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


if sys.argv[0] == "test":
    asyncio.run(get_medal_clip("valorant/clips/DC4NEq0hN_KNe/d1337QdxUXRo"))
else:
    intents = discord.Intents.default()
    intents.message_content = True

    client = MyClient(intents=intents)
    client.run(os.environ.get("TOKEN"))
