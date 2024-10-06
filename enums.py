from enum import Enum


class GameTypes(str, Enum):
    UltraBullet = 'ultraBullet'
    Bullet = 'bullet'
    Blitz = 'blitz'
    Rapid = 'rapid'
    Classical = 'classical'
    Chess960 = 'chess960'
    Crazyhouse = 'crazyhouse'
    Antichess = 'antichess'
    Atomic = 'atomic'
    Horde = 'horde'
    KingOfTheHill = 'kingOfTheHill'
    RacingKings = 'racingKings'
    ThreeCheck = 'threeCheck'
