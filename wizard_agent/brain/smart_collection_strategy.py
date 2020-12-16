from typing import List
import operator
from . import strategy
from .utils import util_functions as utils, constants

'''
Strategy: 

Retreive location of ammo and treasure blocks, 
find the tile with highest score, and get 
corresponding ideal path.

'''


class SmartCollectionStrategy(strategy.Strategy):
    def __init__(self):
        self.ammo_state = {}
        self.prev_bombs = []

        # previous state
        self.prev_item = None
        self.prev_target = None

        self.game_state = None
        self.player_state = None

        # value between 0-1, closer to 1 means it's more likely to go to tile
        self.ammo_priority = 0.5
        self.treasure_priority = 1
        self.reachable_priority = 1

    def execute(self, game_state: object, player_state: object) -> List[str]:
        self.game_state = game_state
        self.player_state = player_state

        location = player_state.location

        # determine if ammo/treasure bomb is within blast zone
        bombs = game_state.bombs

        blast_zone = []

        for bomb in bombs:
            blast_tiles = utils.get_blast_zone(bomb, self.game_state)
            blast_zone += blast_tiles

        ammo_blocks = game_state.ammo
        treasure_blocks = game_state.treasure
        all_location = ammo_blocks + treasure_blocks

        # check if tile in blast zone
        safe_location = [tile for tile in all_location if tile not in blast_zone]

        # retrieve the best tile
        ideal_tile = self.get_ideal_tile(safe_location, ammo_blocks, treasure_blocks, location)

        # navigate to ideal tile
        if ideal_tile is not None:
            self.prev_item = game_state.entity_at(ideal_tile)
            self.prev_target = ideal_tile
            path = utils.get_shortest_path(location, ideal_tile, game_state)
            action_seq = utils.get_path_action_seq(location, path)
            return action_seq

        return [constants.ACTIONS["none"]]

    def can_execute(self, game_state: object, player_state: object) -> bool:
        self.game_state = game_state
        self.player_state = player_state
        self.prev_target = None
        self.prev_item = None

        location = player_state.location
        ammo = player_state.ammo
        ammo_blocks = game_state.ammo
        treasure_blocks = game_state.treasure
        all_location = ammo_blocks + treasure_blocks

        reachable_tiles = utils.get_reachable_tiles(location, all_location, game_state)
        return ammo < 5 and reachable_tiles

    def is_valid(self, game_state: object, player_state: object) -> bool:
        if self.prev_target is not None:
            cur_target_item = game_state.entity_at(self.prev_target)
            return cur_target_item == self.prev_item
        else:
            return True

    def get_ideal_tile(self, all_location, ammo_blocks, treasure_blocks, location):
        opponent_list = self.game_state.opponents(self.player_state.id)
        opponent = utils.get_opponent(location, opponent_list)
        tile_map = self.get_tile_map(all_location, ammo_blocks, treasure_blocks, location)
        p_tile_map = dict(sorted(tile_map.items(), key=operator.itemgetter(1), reverse=True))
        possible_tiles = list(p_tile_map.keys())
        ideal_tile = None
        while len(possible_tiles) > 0:
            tile = possible_tiles.pop(0)
            if not utils.is_opponent_closer(location, opponent, tile, self.game_state):
                ideal_tile = tile
                break
        return ideal_tile

    def get_tile_map(self, all_location, ammo_blocks, treasure_blocks, location):
        tile_map = {}
        for tile in all_location:
            score = self.get_score(tile, ammo_blocks, treasure_blocks, location)
            if tile in tile_map:
                tile_map[tile] += score
            else:
                tile_map[tile] = score
        return tile_map

    def get_score(self, tile, ammo_blocks, treasure_blocks, location):
        path = utils.get_shortest_path(location, tile, self.game_state)
        score = 0

        # ensure that tile is reachable by putting reward / punishment
        if path is not None:
            score += self.reachable_priority
        else:
            score -= self.reachable_priority

        if tile in ammo_blocks:
            score += self.ammo_priority
        if tile in treasure_blocks:
            score += self.treasure_priority

        return score
