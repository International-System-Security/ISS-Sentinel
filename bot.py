import os
import discord
from discord.ext import commands
import requests

BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
SITE_URL = os.environ["SITE_URL"].rstrip("/")      # যেমন https://your-site.onrender.com
STATS_API_KEY = os.environ["STATS_API_KEY"]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


def get_stats():
    r = requests.get(f"{SITE_URL}/api/stats",
                     headers={"X-API-Key": STATS_API_KEY}, timeout=10)
    r.raise_for_status()
    return r.json()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")


@bot.command(name="report")
async def report(ctx):
    try:
        s = get_stats()
        await ctx.send(f"🛡️ ISS Report: system active. Licenses: {s['licenses']} | Open tickets: {s['open_tickets']}")
    except Exception:
        await ctx.send("⚠️ Could not reach the ISS server.")


@bot.command(name="weekly_report")
async def weekly_report(ctx):
    try:
        s = get_stats()
        await ctx.send(f"📈 ISS Weekly Report: {s['licenses']} licenses, {s['open_tickets']} open tickets.")
    except Exception:
        await ctx.send("⚠️ Could not reach the ISS server.")


bot.run(BOT_TOKEN)
