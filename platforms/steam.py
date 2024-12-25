from platforms.base import GamePlatform
from models import Game
import httpx
from bs4 import BeautifulSoup
from typing import List
import logging

class SteamPlatform(GamePlatform):
    async def get_free_games(self) -> List[Game]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get('https://store.steampowered.com/search/?maxprice=free&specials=1')
                if response.status_code != 200:
                    return []

                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                games = []

                for game_div in soup.select('#search_resultsRows a'):
                    title = game_div.select_one('.title')
                    assert title is not None
                    title = title.text.strip()

                    url = game_div['href']
                    if type(url) == str:
                        # Filter out permanent free-to-play games
                        if 'Free To Play' not in game_div.text:
                            game = Game(
                                title=title,
                                url=url,
                                platform='Steam'
                            )
                            games.append(game)
                            logging.info(f'found free game {game.title} on platform="Steam"')

                return games
        except Exception as e:
            logging.error(f"Error fetching Steam games: {e}")
            return []

