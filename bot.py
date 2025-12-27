import os
import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
from database import init_db
from commands.start import register_start_command
from commands.cmds import register_cmds_command
from commands.admin import register_admin_commands
from commands.me import register_me_command
from commands.bin_command import register_bin_command
from commands.credits_command import register_credits_commands
from commands.redeem_command import register_redeem_commands
from commands.plans import register_plans_command
from commands.shopify import register_resource_commands
from dotenv import load_dotenv
from gateways import register_gateways
from utils import Utils
from utils_fo.logger import Logger
from aiohttp import web

BotCache = {}

load_dotenv()

TOKEN = os.environ.get('BOT_TOKEN', '8281283407:AAH5rN5h3OOanofg_SnSFUWrsqM7F_5-k6I')

FREE_USER_LIMIT = int(os.environ.get('FREE_USER_LIMIT', '60'))
PREMIUM_USER_LIMIT = int(os.environ.get('PREMIUM_USER_LIMIT', '20'))
bot = AsyncTeleBot(TOKEN, parse_mode='HTML')

async def init():
    try:
        init_db()
        Utils.load_resources()
        register_start_command(bot)
        register_cmds_command(bot)
        register_admin_commands(bot)
        register_me_command(bot)
        register_bin_command(bot)
        register_credits_commands(bot)
        register_redeem_commands(bot)
        register_plans_command(bot)
        register_resource_commands(bot)
        await register_gateways(bot)
    except Exception as e:
        print(f"Error initializing bot: {e}")

async def clear_previous_updates():
    # Get the latest update id
    updates = await bot.get_updates()
    if updates:
        latest_update_id = max(update.update_id for update in updates)
        await bot.get_updates(offset=latest_update_id + 1)


async def handle_health(request):
    """Simple health endpoint for Render/web platforms."""
    return web.Response(text="OK")


async def start_web_app():
    """
    Start a minimal aiohttp web server bound to PORT.
    This satisfies Render's port scan requirement for Web Services.
    """
    app = web.Application()
    app.router.add_get("/", handle_health)
    app.router.add_get("/health", handle_health)

    port = int(os.environ.get("PORT", "8000"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server running on port {port}")

    # Keep the web server alive
    while True:
        await asyncio.sleep(3600)


async def run_bot():
    """Run Telegram bot polling loop."""
    print("Starting Telegram bot polling...")
    await init()
    # Optionally clear previous updates if needed
    # await clear_previous_updates()
    await bot.polling()


async def main():
    """
    Run both the web server and the Telegram bot in parallel.
    """
    print("Starting web server and Telegram bot...")
    try:
        await asyncio.gather(
            start_web_app(),
            run_bot(),
        )
    except Exception as e:
        print(f"Error running bot/web server: {e}")


if __name__ == '__main__':
    asyncio.run(main())


