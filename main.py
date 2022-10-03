import os
import re

import aiohttp
import discord
from dotenv import load_dotenv

load_dotenv()


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
            clip_path = match.group(1)
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://medal.tv/_next/data/ELKh_LJ4D0_htfA9kVKKA/en/games/{clip_path}.json"
                ) as response:
                    data = await response.json()

            content_url = data["pageProps"]["clip"]["contentUrl"]
            content_title = data["pageProps"]["clip"]["contentTitle"]
            await message.reply(
                f":magic_wand: **{content_title}** {content_url}", mention_author=True
            )
            print(f"Fixed link for {message.author} : {message.content}")
            try:
                await message.edit(suppress=True)
            except discord.errors.Forbidden:
                print("Tried to suppress message but no permissions :(")


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(os.environ.get("TOKEN"))
