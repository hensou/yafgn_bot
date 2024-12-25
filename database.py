import sqlite3
from models import Game
from datetime import datetime

class Database:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    title TEXT,
                    url TEXT,
                    platform TEXT,
                    end_date TEXT,
                    PRIMARY KEY (title, platform)
                )
            """)

    def add_game(self, game: Game) -> bool:
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO games VALUES (?, ?, ?, ?)",
                    (game.title, game.url, game.platform,
                     game.end_date.isoformat() if game.end_date else None)
                )
                return conn.total_changes > 0
        except sqlite3.Error:
            return False

    def is_game_exists(self, game: Game) -> bool:
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM games WHERE title = ? AND platform = ?",
                (game.title, game.platform)
            )
            return cursor.fetchone() is not None

    def games_from_date(self, datetime: datetime):
        games : list[Game] = []
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.execute(
                "SELECT * FROM games WHERE end_date >= ?",
                (datetime.isoformat(),)
            )
            for row in cursor.fetchall():
                games.append(
                    Game(
                        title=row[0],
                        url=row[1],
                        platform=row[2],
                        end_date=datetime.fromisoformat(row[3])
                    )
                )

        return games

