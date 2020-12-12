from . import constants
from . import structures

ACTIONS = constants.ACTIONS
Node = structures.Node


def manhattan_distance(start, end):
    """
    returns the manhattan distance between two tiles, calculated as:
    |x1 - x2| + |y1 - y2|
    """
    distance = abs(start[0] - end[0]) + abs(start[1] - end[1])
    return distance


def get_surrounding_tiles(location, game_state):
    """Given a tile location as an (x,y) tuple, this function will return the surrounding tiles up, down, left and to
    the right as a list (i.e. [(x1,y1), (x2,y2),...]) as long as they do not cross the edge of the map """
    x = location[0]
    y = location[1]

    # find all the surrounding tiles relative to us
    # location[0] = col index; location[1] = row index
    tile_up = (x, y - 1)
    tile_down = (x, y + 1)
    tile_left = (x - 1, y)
    tile_right = (x + 1, y)

    # combine these int a list
    all_surrounding_tiles = [tile_up, tile_down, tile_right, tile_left]

    # get ones that are within bounds
    valid_surrounding_tiles = []

    for tile in all_surrounding_tiles:
        if game_state.is_in_bounds(tile):
            valid_surrounding_tiles.append(tile)

    return valid_surrounding_tiles


def get_empty_tiles(tiles, game_state):
    """
    Given a list of tiles, return ones that are actually empty
    """
    empty_tiles = []

    for tile in tiles:
        if not game_state.is_occupied(tile):
            empty_tiles.append(tile)

    return empty_tiles


def get_safest_tile(location, tiles, bombs):
    """
    Given a list of tiles and bombs, find the tile that's safest to move to
    """

    bomb_distance = 10
    closest_bomb = bombs[0]

    for bomb in bombs:
        new_bomb_distance = manhattan_distance(bomb, location)
        if new_bomb_distance < bomb_distance:
            bomb_distance = new_bomb_distance
            closest_bomb = bomb

    safe_dict = {}
    for tile in tiles:
        distance = manhattan_distance(closest_bomb, tile)
        safe_dict[tile] = distance

    # return the tile with the furthest distance from any bomb
    safest_tile = max(safe_dict, key=safe_dict.get)

    return safest_tile


def move_to_tile(location, tile):
    """
    Determines the action based on the tile. The other tile must be adjacent to the location tile
    """
    diff = tuple(x - y for x, y in zip(location, tile))

    if diff == (0, 1):
        return ACTIONS["down"]
    elif diff == (1, 0):
        return ACTIONS["left"]
    elif diff == (0, -1):
        return ACTIONS["up"]
    elif diff == (-1, 0):
        return ACTIONS["right"]
    else:
        return ACTIONS["none"]


def get_shortest_path(start, end, game_state):
    """
    Finds the shortest path from the start node to the end node.
    Returns an array of (x,y) tuples. Uses A* search algorithm
    """
    # create a list for all nodes to visit and have been visited
    queue = []
    visited = []

    # create a start node and end node
    start_node = Node(start, None)
    goal_node = Node(end, None)

    queue.append(start_node)

    while len(queue) > 0:
        # sort the open list to get the node with the lowest cost first
        queue.sort()

        # get the node with the lowest cost
        current_node = queue.pop(0)

        # add the current node to the closed list
        visited.append(current_node)

        # check if we have reached the goal, return the path
        if current_node == goal_node:
            path = []
            while current_node != start_node:
                path.append(current_node.position)
                current_node = current_node.parent
            # return reversed
            return path[::-1]

        # loop through each neighbour
        neighbours = get_surrounding_tiles(current_node.position, game_state)

        for tile in neighbours:
            if not is_walkable(tile, game_state):
                continue  # skip if not walkable

            neighbour = Node(tile, current_node)

            if neighbour in visited:
                continue  # skip if visited

            # generate heuristics
            neighbour.dist_to_start = manhattan_distance(neighbour.position, start_node.position)
            neighbour.dist_to_goal = manhattan_distance(neighbour.position, goal_node.position)
            neighbour.total_cost = neighbour.dist_to_start + neighbour.dist_to_goal

            # check if neighbour is in the open list and if it has a lower total value
            if can_enqueue(queue, neighbour):
                queue.append(neighbour)

    return None  # no path found


def is_walkable(tile, game_state):
    """
    Returns true if the tile is walkable
    """
    collectible = ["a", "t"]
    return not game_state.is_occupied(tile) or game_state.entity_at(tile) in collectible


def can_enqueue(queue, neighbour):
    """
    Helper function for the A* search algorithm. Checks if neighbour is in
    the queue and if it has lower total value
    """
    for node in queue:
        if neighbour == node and neighbour.total_cost >= node.total_cost:
            return False
    return True
