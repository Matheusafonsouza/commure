from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from models.rating_history import RatingHistory

BASE_PATH = "services.chess"


@patch(f"{BASE_PATH}.requests.get")
def test_fetch_success(get_mock, chess_service_fixture):
    expected = {"ok": True}
    endpoint = "test"
    get_mock.return_value.json.return_value = expected
    result = chess_service_fixture._fetch(endpoint)
    assert expected == result
    get_mock.assert_called_with("https://lichess.org/api/test")
    get_mock.return_value.raise_for_status.assert_called()
    get_mock.return_value.json.assert_called()


@patch(f"{BASE_PATH}.requests.get")
def test_fetch_failure(get_mock, chess_service_fixture):
    endpoint = "test"
    get_mock.return_value.raise_for_status.side_effect = Exception()

    with pytest.raises(Exception):
        chess_service_fixture._fetch(endpoint)

    get_mock.assert_called_with("https://lichess.org/api/test")
    get_mock.return_value.raise_for_status.assert_called()
    get_mock.return_value.json.assert_not_called()


@patch(f"{BASE_PATH}.ChessService._fetch")
def test_get_player_rating_history(
    fetch_mock, chess_service_fixture, generate_rating_history_fixture
):
    fetch_mock.return_value = [
        {"name": "name1", "points": [[2023, 1, 1, 2000]]},
        {"name": "name2", "points": [[2023, 1, 1, 2000]]},
    ]

    username = "username"
    result = chess_service_fixture._get_player_rating_history(username)

    fetch_mock.assert_called_with(f"user/{username}/rating-history")

    assert result == [
        generate_rating_history_fixture("name1"),
        generate_rating_history_fixture("name2"),
    ]


@pytest.mark.parametrize(
    "type,expected",
    [
        (
            "name1",
            RatingHistory(
                name="name1",
                points=[[2023, 1, 1, 2000]],
            ),
        ),
        ("name3", None),
    ],
)
@patch(f"{BASE_PATH}.ChessService._get_player_rating_history")
def test_get_player_type_rating_history(
    get_player_rating_history_mock,
    type,
    expected,
    chess_service_fixture,
    generate_rating_history_fixture,
):
    get_player_rating_history_mock.return_value = [
        generate_rating_history_fixture(name="name1"),
        generate_rating_history_fixture(name="name2"),
    ]

    username = "username"
    result = chess_service_fixture._get_player_type_rating_history(
        username,
        type,
    )

    get_player_rating_history_mock.assert_called_with(username)
    assert result == expected


@patch(f"{BASE_PATH}.ChessService._fetch")
def test_get_top_players(
    fetch_mock,
    chess_service_fixture,
    generate_player_fixture,
):
    fetch_mock.return_value = {
        "users": [
            {"username": "username1"},
            {"username": "username2"},
        ]
    }

    length = 2
    type = "name1"
    result = chess_service_fixture.get_top_players(length, type)

    fetch_mock.assert_called_with(f"player/top/{length}/{type}")

    assert result == [
        generate_player_fixture(username="username1"),
        generate_player_fixture(username="username2"),
    ]


@patch(f"{BASE_PATH}.ChessService._get_player_type_rating_history")
def test_get_last_days_player_rating_history_points(
    get_player_type_rating_history_mock,
    chess_service_fixture,
    generate_rating_history_fixture,
):
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    history = generate_rating_history_fixture(
        name="name1",
        points=[
            [now.year, now.month - 1, now.day, 2000],
            [yesterday.year, yesterday.month - 1, yesterday.day, 2000],
        ],
    )
    get_player_type_rating_history_mock.return_value = history

    type = "name1"
    username = "username1"
    result = chess_service_fixture.get_last_days_player_rating_history_points(
        username, type, 2
    )

    get_player_type_rating_history_mock.assert_called_with(username, type)

    assert result == {"2024-10-05": 2000, "2024-10-06": 2000}


@patch(f"{BASE_PATH}.ChessService._get_player_type_rating_history")
def test_get_last_days_player_rating_history_points_no_history(
    get_player_type_rating_history_mock,
    chess_service_fixture,
):
    get_player_type_rating_history_mock.return_value = None

    type = "name1"
    username = "username1"
    result = chess_service_fixture.get_last_days_player_rating_history_points(
        username, type, 2
    )

    get_player_type_rating_history_mock.assert_called_with(username, type)

    assert result == {}


@patch(f"{BASE_PATH}.pd")
@patch(f"{BASE_PATH}.ChessService.get_last_days_player_rating_history_points")
@patch(f"{BASE_PATH}.ChessService.get_top_players")
def test_save_players_rating_history_csv(
    get_top_players_mock,
    get_last_days_player_rating_history_points_mock,
    pandas_mock,
    chess_service_fixture,
    generate_player_fixture,
):
    get_top_players_mock.return_value = [
        generate_player_fixture(username="username1"),
    ]
    get_last_days_player_rating_history_points_mock.return_value = {
        "2023-1-1": 2000,
    }

    length = 1
    type = "name1"
    chess_service_fixture.save_players_rating_history_csv(length, type)

    get_top_players_mock.assert_called_with(length, type)
    get_last_days_player_rating_history_points_mock.assert_called_with(
        "username1", type, 30
    )
    pandas_mock.DataFrame.return_value.to_csv.assert_called_with(
        "histories.csv", sep=",", encoding="utf-8", index=False
    )
