from os import makedirs
from enum import Enum
from math import *

DEBUG = 0


class Action(Enum):
    def __str__(self) -> str:
        return str(self.value)

    STAY = 0
    MOVE_DOWN = 1
    MOVE_UP = 2
    MOVE_RIGHT = 3
    MOVE_LEFT = 4
    UPGRADE_DEFENCE = 5
    UPGRADE_ATTACK = 6
    LINEAR_ATTACK_DOWN = 7
    LINEAR_ATTACK_UP = 8
    LINEAR_ATTACK_RIGHT = 9
    LINEAR_ATTACK_LEFT = 10
    RANGED_ATTACK = 11


class MapType(Enum):
    def __str__(self) -> str:
        return str(self.value)

    EMPTY = 0
    AGENT = 1
    GOLD = 2
    TREASURY = 3
    WALL = 4
    FOG = 5
    OUT_OF_SIGHT = 6
    OUT_OF_MAP = 7


class MapTile:
    def __init__(self) -> None:
        self.type: MapType
        self.data: int
        self.coordinates: tuple(int, int)

    def __str__(self) -> str:
        res = self.type.name
        if self.type in [MapType.OUT_OF_SIGHT, MapType.OUT_OF_MAP]:
            return res.center(16)
        elif self.type in [MapType.AGENT, MapType.GOLD]:
            res += f':{self.data}'
        res += f' ({self.coordinates[0]},{self.coordinates[1]})'
        return res.center(16)


class Map:
    def __init__(self) -> None:
        self.width: int
        self.height: int
        self.gold_count: int
        self.sight_range: int
        self.grid: list

    def __str__(self) -> str:
        res = f'sight range -> {self.sight_range}\n'
        for i in range(self.sight_range):
            res += '\t'
            for j in range(self.sight_range):
                res += str(self.grid[i * self.sight_range + j])
                res += '*' if j < 4 else '\n'
        return res[:-1]

    def set_grid_size(self) -> None:
        self.grid = [MapTile() for _ in range(self.sight_range ** 2)]


def write_logs_line(message) -> None:
    fileName = 'text.txt'
    with open(fileName, 'a') as f:
        f.write(message)
        f.write("\n")
def write_logs_table(table) -> None:
    fileName = 'text.txt'
    with open(fileName, 'a') as f:
        for row in table:
            f.write(str(row))
            f.write('\n')
        f.write('-' * 20)
        f.write('\n')

class GameState:
    def __init__(self) -> None:
        self.rounds = int(input())
        self.def_upgrade_cost = int(input())
        self.atk_upgrade_cost = int(input())
        self.cool_down_rate = float(input())
        self.linear_attack_range = int(input())
        self.ranged_attack_radius = int(input())
        self.map = Map()
        self.map.width, self.map.height = map(int, input().split())
        self.map.gold_count = int(input())
        self.map.sight_range = int(input())  # equivalent to (2r+1)
        self.map.set_grid_size()
        self.ai = AI(self.map.width, self.map.height)
        self.debug_log = ''

    def set_info(self) -> None:
        self.location = tuple(map(int, input().split()))  # (row, column)
        for tile in self.map.grid:
            tile.type, tile.data, *tile.coordinates = map(int, input().split())
            tile.type = MapType(tile.type)
        self.agent_id = int(input())  # player1: 0,1 --- player2: 2,3
        self.current_round = int(input())  # 1 indexed
        self.attack_ratio = float(input())
        self.deflvl = int(input())
        self.atklvl = int(input())
        self.wallet = int(input())
        self.safe_wallet = int(input())
        self.wallets = [*map(int, input().split())]  # current wallet
        self.last_action = int(input())  # -1 if unsuccessful

    def debug(self) -> None:
        # Customize to your needs
        self.debug_log += f'round: {str(self.current_round)}\n'
        self.debug_log += f'location: {str(self.location)}\n'
        self.debug_log += f'Map: {str(self.map)}\n'
        self.debug_log += f'attack ratio: {str(self.attack_ratio)}\n'
        self.debug_log += f'defence level: {str(self.deflvl)}\n'
        self.debug_log += f'attack level: {str(self.atklvl)}\n'
        self.debug_log += f'wallet: {str(self.wallet)}\n'
        self.debug_log += f'safe wallet: {str(self.safe_wallet)}\n'
        self.debug_log += f'list of wallets: {str(self.wallets)}\n'
        self.debug_log += f'last action: {str(self.last_action)}\n'
        self.debug_log += f'{60 * "-"}\n'

    def debug_file(self) -> None:
        fileName = 'Clients/logs/'
        makedirs(fileName, exist_ok=True)
        fileName += f'AGENT{self.agent_id}.log'
        with open(fileName, 'a') as f:
            f.write(self.debug_log)

    def get_action(self) -> Action:
        # write your code here
        # return the action value
        self.ai.recon(self.agent_id, self.location, self.map)
        write_logs_table(self.ai.plot)
        # self.write_logs(self.map.__str__())
        return Action.MOVE_DOWN


class AI:
    def __init__(self, map_width: int, map_height: int) -> None:
        self.enemy_agents = None
        self.our_agents = None
        self.plot = [[-2 for _ in range(map_width)] for _ in range(map_height)]

    def recon(self, agent_id: int, location: tuple, recon_map: Map) -> None:
        for tile in recon_map.grid:
            if tile.type not in [MapType.OUT_OF_MAP, MapType.OUT_OF_SIGHT]:
                if tile.type == MapType.AGENT:
                    data = str(tile.data)
                    for row in range(len(self.plot)):
                        if data in self.plot[row]:
                            self.plot[row][self.plot[row].index(data)] = -2
                    self.plot[tile.coordinates[0]][tile.coordinates[1]] = data
                elif tile.type == MapType.GOLD:
                    self.plot[tile.coordinates[0]][tile.coordinates[1]] = 4
                elif tile.type == MapType.EMPTY:
                    self.plot[tile.coordinates[0]][tile.coordinates[1]] = -1
                elif tile.type == MapType.FOG:
                    self.plot[tile.coordinates[0]][tile.coordinates[1]] = 5
                elif tile.type == MapType.TREASURY:
                    self.plot[tile.coordinates[0]][tile.coordinates[1]] = 7
                elif tile.type == MapType.WALL:
                    self.plot[tile.coordinates[0]][tile.coordinates[1]] = 6
                self.plot[location[0]][location[1]] = agent_id

    def set_agents(self, our_agents: list, enemy_agents: list):
        self.our_agents = our_agents
        self.enemy_agents = enemy_agents

    def distance(self, pos1: tuple, pos2: tuple) -> float:
        return sqrt(pow(pos1[0] - pos2[0], 2) + pow(pos1[1] - pos2[1], 2))

    UNKNOWN = -2
    EMPTY = -1
    AGENT0 = 0
    AGENT1 = 1
    AGENT2 = 2
    AGENT3 = 3
    GOLD = 4
    FOG = 5
    WALL = 6
    TREASURY = 7

if __name__ == '__main__':
    game_state = GameState()
    for _ in range(game_state.rounds):
        game_state.set_info()
        print(game_state.get_action())
        if DEBUG:
            game_state.debug()
    if DEBUG:
        game_state.debug_file()
