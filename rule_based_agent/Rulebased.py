# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com

import random
import typing
from step_0_state_attributes import make_training_example

# Step 1 enables recording; normal play and Step 4 do not write datasets.
recording_enabled = True
recording_seed = None
recorded_rows = []


def record_state(game_state: typing.Dict, direction: str):
    """Store one example using the shared schema in step_0_state_attributes.py."""
    recorded_rows.append(make_training_example(
        game_state, direction, seed=recording_seed, label_source="rule_based_agent"
    ))


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    #print("INFO")

    return {
        "apiversion": "1",
        "author": "sneaky snake",  # TODO: Your Battlesnake Username
        "color": "#888888",  #z TODO: Choose color
        "head": "default",  # TODO: Choose head
        "tail": "default",  # TODO: Choose tail
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:

    is_move_safe = {"up": True, "down": True, "left": True, "right": True}

    # We've included code to prevent your Battlesnake from moving backwards
    my_head = game_state["you"]["body"][0]  # Coordinates of your head
    my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"

    if my_neck["x"] < my_head["x"]:  # Neck is left of head, don't move left
        is_move_safe["left"] = False

    elif my_neck["x"] > my_head["x"]:  # Neck is right of head, don't move right
        is_move_safe["right"] = False

    elif my_neck["y"] < my_head["y"]:  # Neck is below head, don't move down
        is_move_safe["down"] = False

    elif my_neck["y"] > my_head["y"]:  # Neck is above head, don't move up
        is_move_safe["up"] = False

    # TODO: Step 1 - Prevent your Battlesnake from moving out of bounds
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']

    # The tiles before the outside border of the game
    top_border = board_height-1
    bottom_border = 0
    right_border = board_width-1
    left_border = 0

    if my_head["y"] == top_border:
        is_move_safe["up"] = False
    elif my_head["y"] == bottom_border:
        is_move_safe["down"] = False

    if my_head["x"] == right_border:
        is_move_safe["right"] = False
    elif my_head["x"] == left_border:
        is_move_safe["left"] = False

    # TODO: Step 2 - Prevent your Battlesnake from colliding with itself
    my_body = game_state['you']['body'][2:] # Ignore head and neck

    for body in my_body:
        if my_head["y"] == body["y"]:
            if my_head["x"]+1 == body["x"]:
                is_move_safe["right"] = False
            if my_head["x"]-1 == body["x"]:
                is_move_safe["left"] = False
        if my_head["x"] == body["x"]:
            if my_head["y"]+1 == body["y"]:
                is_move_safe["up"] = False
            if my_head["y"]-1 == body["y"]:
                is_move_safe["down"] = False


    # TODO: Step 3 - Prevent your Battlesnake from colliding with other Battlesnakes
    opponents = game_state['board']['snakes']

    for opponent in opponents:
        if opponent == ['you']:
            print("this was called") # silent error not being called atm.
            continue



        for enemy_body in opponent['body']:
            if my_head["y"] == enemy_body["y"]:
                if my_head["x"]+1 == enemy_body["x"]:
                    is_move_safe["right"] = False
                if my_head["x"]-1 == enemy_body["x"]:
                    is_move_safe["left"] = False
            if my_head["x"] == enemy_body["x"]:
                if my_head["y"]+1 == enemy_body["y"]:
                    is_move_safe["up"] = False
                if my_head["y"]-1 == enemy_body["y"]:
                    is_move_safe["down"] = False

    # Are there any safe moves left?
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)

    if len(safe_moves) == 0:
        #print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}

    # Choose a random move from the safe ones
    next_move = random.choice(safe_moves)

    # TODO: Step 4 - Move towards food instead of random, to regain health and survive longer
    food_all = game_state['board']['food']
    saturation = game_state['you']['health']
    prioritise_food = 100

    closest_food = None
    closest_distance = 10000


    if saturation <= prioritise_food:

        # Find the closest food
        for food in food_all:
            food_distance = abs(food["x"]-my_head["x"])
            food_distance += abs(food["y"]-my_head["y"])
            #print(f"food distance: {food_distance}")
            if food_distance < closest_distance:
                closest_distance = food_distance
                closest_food = food

        possible_moves = []

        if closest_food["x"] > my_head["x"]:
            if is_move_safe["right"]:
                possible_moves.append("right")

        elif closest_food["x"] < my_head["x"]:
            if is_move_safe["left"]:
                possible_moves.append("left")

        elif closest_food["y"] > my_head["y"]:
            if is_move_safe["up"]:
                possible_moves.append("up")

        elif closest_food["y"] < my_head["y"]:
            if is_move_safe["down"]:
                possible_moves.append("down")

        if len(possible_moves)> 0:
            next_move = random.choice(possible_moves)

        #for move in possible_moves:
            #if is_move_safe[move]:
                #next_move = move

    if recording_enabled:
        record_state(game_state, next_move)

    #print(f"MOVE {game_state['turn']}: {next_move}")
    return {"move": next_move}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
