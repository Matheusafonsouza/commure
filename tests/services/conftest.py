from typing import List

import pytest

from models.player import Player
from models.rating_history import RatingHistory
from services.chess import ChessService


@pytest.fixture
def chess_service_fixture():
    return ChessService()


@pytest.fixture
def generate_player_fixture():
    def _generate_player(username: str) -> Player:
        return Player(username=username)

    return _generate_player


@pytest.fixture
def generate_rating_history_fixture():
    def _generate_rating_history(
        name: str, points: List[List[int]] = None
    ) -> RatingHistory:
        points = points or [[2023, 1, 1, 2000]]
        return RatingHistory(name=name, points=points)

    return _generate_rating_history
