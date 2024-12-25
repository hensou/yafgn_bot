# platforms/epic.py
from platforms.base import GamePlatform
from models import Game
import httpx
from typing import List
from datetime import datetime
import logging

class EpicGamesPlatform(GamePlatform):
    EPIC_API_URL = 'https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions'

    async def get_free_games(self) -> List[Game]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.EPIC_API_URL)
                if response.status_code != 200:
                    return []

                data = response.json()
                games = []

                for game in data.get('data', {}).get('Catalog', {}).get('searchStore', {}).get('elements', []):
                    if game.get('promotions'):
                        promotions = game['promotions']['promotionalOffers']
                        if promotions and promotions[0]['promotionalOffers']:
                            promo = promotions[0]['promotionalOffers'][0]
                            discount_percentage = promo['discountSetting']['discountPercentage']
                            if discount_percentage == 0 or discount_percentage == 100:
                                end_date = datetime.fromisoformat(promo['endDate'].replace('Z', '+00:00'))
                                game = Game(
                                    title=game['title'],
                                    url=f"https://store.epicgames.com/p/{game['productSlug']}",
                                    platform='Epic Games',
                                    end_date=end_date,
                                    description=game.get('description')
                                )
                                logging.info(f"found free game {game.title=} on plataform='Epic Games'")
                                games.append(game)

                return games
        except Exception as e:
            logging.error(f"Error fetching Epic games: {e}", exc_info=e)
            return []

