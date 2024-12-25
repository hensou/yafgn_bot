from dotenv import load_dotenv
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from database import Database
from platforms.steam import SteamPlatform
from platforms.epic import EpicGamesPlatform
from datetime import datetime

from models import Game

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))  # Default 1 hour
DATABASE_FILE = os.getenv('DATABASE_PATH', 'games.db')


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class FreeGamesBot:
    def __init__(self):
        self.db = Database(DATABASE_FILE)
        self.platforms = [
            SteamPlatform(),
            EpicGamesPlatform(),
        ]
        self.active_chats = set()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command"""
        chat = update.effective_chat
        message = update.effective_message
        assert chat != None
        assert message != None

        chat_id = chat.id
        self.active_chats.add(chat_id)
        await context.bot.send_message(
            chat_id=chat_id,
            text="👋 Welcome to Yet Another Free Games Notifier Bot (@yafgn_bot)!\n"
                 "I'll periodicly notify you about free games from various platforms.\n"
                 "Currently, I check on Steam and EpicGames.\n"
                 "If you want to ask or contribute with other plataforms create an issue at https://github.com/hensou/yafgn_bot .\n"
                 "You can also use /check to manually check for free games."
        )

        games = await self._get_current_games(message.date)
        
        if len(games) > 0:
            await context.bot.send_message(
                chat_id=chat_id,
                text="🎮 Here are some free games you can redeem now!\n",
            )
            for game in games:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=game.to_message(),
                    parse_mode='Markdown',
                    disable_web_page_preview=False
                )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Currently there is not free game that you can redeem today, but I'll tell you in case there new ones.\n",
            )
    async def _get_current_games(self, datetime: datetime) -> list[Game]:
        games = self.db.games_from_date(datetime)
        return games


    async def check_games(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /check command"""
        chat = update.effective_chat
        assert chat != None
        chat_id = chat.id
        await context.bot.send_message(
            chat_id=chat_id,
            text="🔍 Checking for free games..."
        )
        
        new_games = await self._fetch_and_filter_games()
        
        if not new_games:
            await context.bot.send_message(
                chat_id=chat_id,
                text="No new free games found at the moment."
            )
            return

        for game in new_games:
            await context.bot.send_message(
                chat_id=chat_id,
                text=game.to_message(),
                parse_mode='Markdown',
                disable_web_page_preview=False
            )

    async def _fetch_and_filter_games(self):
        """Fetch games from all platforms and filter out existing ones"""
        new_games = []
        
        for platform in self.platforms:
            try:
                games = await platform.get_free_games()
                for game in games:
                    if not self.db.is_game_exists(game):
                        if self.db.add_game(game):
                            new_games.append(game)
            except Exception as e:
                logger.error(f"Error processing platform {platform.__class__.__name__}: {e}", exc_info=e)
                
        return new_games

    async def periodic_check(self, context: ContextTypes.DEFAULT_TYPE):
        """Periodically check for new games and notify all active chats"""
        new_games = await self._fetch_and_filter_games()

        if new_games:
            for chat_id in self.active_chats:
                for game in new_games:
                    try:
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=game.to_message(),
                            parse_mode='Markdown',
                            disable_web_page_preview=False
                        )
                    except Exception as e:
                        logger.error(f"Error sending message to chat {chat_id}: {e}")
                        self.active_chats.discard(chat_id)

def main():
    """Start the bot"""
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    bot = FreeGamesBot()

    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("check", bot.check_games))

    job_queue = application.job_queue
    assert job_queue is not None

    job_queue.run_repeating(bot.periodic_check, interval=CHECK_INTERVAL, first=10)
    application.run_polling()

if __name__ == '__main__':
    main()
