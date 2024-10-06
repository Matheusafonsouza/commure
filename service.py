from typing import List, Optional
from datetime import datetime, timedelta

import requests
import pandas as pd
from tqdm import tqdm
from pydantic import TypeAdapter
from urllib.parse import urljoin

from constants import API_URL
from models.rating_history import RatingHistory
from models.player import Player


class ChessService:
    def __init__(self) -> None:
        self.base_url = API_URL

    def _fetch(self, endpoint: str) -> dict:
        response = requests.get(urljoin(self.base_url, endpoint))
        response.raise_for_status()
        return response.json()

    def _get_player_rating_history(self, username: str) -> List[RatingHistory]:
        return TypeAdapter(List[RatingHistory]).validate_python(
            self._fetch(f"user/{username}/rating-history")
        )

    def _get_player_type_rating_history(self, username: str, type: str) -> Optional[RatingHistory]:
        for rating in self._get_player_rating_history(username):
            if rating.name.lower() == type:
                return rating
        return None
            
    def get_top_players(self, length: int, type: str) -> List[Player]:
        data = self._fetch( f"player/top/{length}/{type}")
        return TypeAdapter(List[Player]).validate_python(data.get("users"))

    def get_last_days_player_rating_history_points(self, username: str, type: str, days: int) -> dict:
        history = self._get_player_type_rating_history(
            username,
            type,
        )
        if not history:
            return {}
        
        score = 0
        point_hashmap = {f"{point[0]}{point[1]+1}{point[2]}": point[3] for point in history.points}

        days_count = days

        hashmap = {}
        for index in range(days_count):
            date = (datetime.now() - timedelta(days=days_count-index-1)).date()
            score = point_hashmap.get(f"{date.year}{date.month}{date.day}") or score
            hashmap[date.strftime("%Y-%m-%d")] = score

        return hashmap

    def save_players_rating_history_csv(self, length: int, type: str) -> None:
        histories = []

        for player in tqdm(self.get_top_players(length, type)):
            history = self.get_last_days_player_rating_history_points(
                player.username,
                type,
                30,
            )
            history["username"] = player.username
            histories.append(history)

        df = pd.DataFrame(histories)
        df.insert(0, "username", df.pop("username"))
        df.to_csv("test.csv", sep=",", encoding="utf-8", index=False)
