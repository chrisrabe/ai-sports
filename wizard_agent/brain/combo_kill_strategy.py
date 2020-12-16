from typing import List

from .strategy import Strategy
from .utils import util_functions as utils, constants
import random


class ComboKillStrategy(Strategy):
    def execute(self, game_state: object, player_state: object) -> List[str]:
        print('combo kill')
        location = player_state.location
        opponent_list = game_state.opponents(player_state.id)
        opponent = utils.get_opponent(location, opponent_list)
        # grabs empty tiles near opponent
        surrounding_tiles = utils.get_surrounding_empty_tiles(opponent, game_state)

        reachable_tiles = utils.get_reachable_tiles(location, surrounding_tiles, game_state)
        nearest_tile = utils.get_nearest_tile(location, reachable_tiles)
        # navigate to nearest empty tile
        if nearest_tile is not None:
            path = utils.get_shortest_path(location, nearest_tile, game_state)
            action_seq = utils.get_path_action_seq(location, path)

            shots = player_state.ammo
            for i in range(shots):
                action_seq.append(constants.ACTIONS["bomb"])
            return action_seq
        return [constants.ACTIONS["none"]]

    def can_execute(self, game_state: object, player_state: object) -> bool:
        location = player_state.location
        opponent_list = game_state.opponents(player_state.id)
        opponent = utils.get_opponent(location, opponent_list)
        ammo = player_state.ammo
        # grabs empty tiles near opponent
        opponent_surroundings = utils.get_surrounding_tiles(opponent, game_state)
        non_walkable_items = ['b', 'ob', 'ib', 'sb']
        
        check_opponent_surroundings = [True for tile in opponent_surroundings if game_state.entity_at(tile) in non_walkable_items]
        # print(check_opponent_surroundings)
        if sum(check_opponent_surroundings) > 0:
            surrounding_empty_tiles = utils.get_surrounding_empty_tiles(opponent, game_state)
            reachable_tiles = utils.get_reachable_tiles(location, surrounding_empty_tiles, game_state)
        else:
            surrounding_empty_tiles = utils.get_surrounding_empty_tiles(opponent, game_state)
            reachable_tiles = False          
        # execute when player has ammo and there's a reachable tile to opponent
        return ammo >= 2 and reachable_tiles
