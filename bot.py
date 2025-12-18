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
from aiohttp import web
import os

from dotenv import load_dotenv
import os

load_dotenv()


from gateways import register_gateways
from utils import Utils
from utils_fo.logger import Logger
BotCache = {}

TOKEN = '7353518607:AAF2faMUxZriRhXw6tAdDYrM752J_lLjv_k'

FREE_USER_LIMIT = int(os.environ.get('FREE_USER_LIMIT', '60'))
PREMIUM_USER_LIMIT = int(os.environ.get('PREMIUM_USER_LIMIT', '20'))
bot = AsyncTeleBot(TOKEN, parse_mode='HTML')

# Create a simple web server for Render health checks
async def health_check(request):
    return web.Response(text='Bot is running')

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    
    # Get port from Render environment variable
    port = int(os.environ.get('PORT', 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")
    return runner

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

async def main():
    # Start web server for Render health checks
    web_runner = await start_web_server()
    
    print("Bot starting...")
    try:
        await init()
        
        # Run bot polling and web server concurrently
        await asyncio.gather(
            bot.polling(non_stop=True, interval=0, timeout=20),
            return_exceptions=True
        )
    except Exception as e:
        print(f"Error running bot: {e}")
    finally:
        await web_runner.cleanup()

if __name__ == '__main__':
    asyncio.run(main())
