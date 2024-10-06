from enums.game_types import GameTypes
from services.chess import ChessService

service = ChessService()


def print_top_50_classical_players() -> None:
    for player in service.get_top_players(50, GameTypes.Classical):
        print(player.username)


def print_last_30_day_rating_for_top_player() -> None:
    top_player = service.get_top_players(1, GameTypes.Classical)[0]
    last_30_days_points = service.get_last_days_player_rating_history_points(
        top_player.username,
        GameTypes.Classical,
        30,
    )
    print(last_30_days_points)


def save_top_50_classical_csv() -> None:
    service.save_players_rating_history_csv(50, GameTypes.Classical)


def main() -> None:
    print_top_50_classical_players()
    # print_last_30_day_rating_for_top_player()
    # save_top_50_classical_csv()


if __name__ == "__main__":
    main()
