"""Shared Battlesnake attributes and training examples, independent of any agent.

Edit state_to_attributes() to select recorded features and INPUT_COLUMNS to
select numeric network inputs. Recording, training and live inference all use
this schema. Other agents can import these helpers without importing a bot or
starting the simulator.
"""
import copy
from pathlib import Path

import pandas as pd


ACTIONS = ["up", "down", "left", "right"]
DELTAS = {"up": (0, 1), "down": (0, -1), "left": (-1, 0), "right": (1, 0)}

# These numeric columns are the network's inputs. The complete apple list and
# original state are also recorded, but variable-length lists are not MLP inputs.
INPUT_COLUMNS = ["board_width",
                 "board_height",
                 "saturation",
                 "current_direction_x",
                 "current_direction_y",
                 "safe_up",
                 "safe_down",
                 "safe_left",
                 "safe_right",
                 "apple_absolute_x",
                 "apple_absolute_y",
                 "apple_relative_x",
                 "apple_relative_y",
                 "apple_distance",
                 "length"]

def state_to_attributes(state):
    """OPTIONAL TASK: add attributes here; add numeric inputs to INPUT_COLUMNS.

    Step 3 calls this exact function during live play. Safe means inside the
    board and outside all current body cells. Tails are treated as occupied.
    This does not predict future traps or simultaneous head-to-head collisions.
    """
    board, snake = state["board"], state["you"]
    attributes = {"board_width": board["width"], "board_height": board["height"]}


    # hp
    attributes['saturation'] = snake["health"]

    # head direction
    head = snake["body"][0]
    neck = snake["body"][1]

    current_direction_x = head["x"] - neck["x"]
    current_direction_y = head["y"] - neck["y"]

    attributes['current_direction_x'] = current_direction_x
    attributes['current_direction_y'] = current_direction_y

    # Snake length
    length = len(snake["body"])
    attributes['length'] = length

    # Obstacles
    safe_moves = get_safe_moves(state)

    attributes['safe_up'] = safe_moves['up']
    attributes['safe_down'] = safe_moves['down']
    attributes['safe_left'] = safe_moves['left']
    attributes['safe_right'] = safe_moves['right']

    # Food position
    food_all = board["food"]
    closest_food = None
    closest_distance = 10000

    # Find the closest food
    for food in food_all:
        food_distance = abs(food["x"] - head["x"])
        food_distance += abs(food["y"] - head["y"])

        if food_distance < closest_distance:
            closest_distance = food_distance
            closest_food = food
    attributes['apple_absolute_x'] = closest_food["x"]
    attributes['apple_absolute_y'] = closest_food["y"]
    attributes['apple_distance'] = closest_distance

    attributes['apple_relative_x'] = closest_food["x"] - head["x"]
    attributes['apple_relative_y'] =closest_food["y"] - head["y"]


    # TODO: add further attributes you want to track. For each attribute, also add the
    #  name of the attribute in the list called INPUT_COLUMNS above.

    # TODO: add the following two code lines at the bottom of the action selection
    #  function of your rule-based agent right before it returns the next_move of your snake.
    #  ```
    #       if recording_enabled:
    #           record_state(game_state, next_move)
    #  ```
    #  This will ensure that the following files work as expected.

    return attributes

def get_safe_moves(state):
    board = state["board"]
    snake = state["you"]

    # The tiles before the outside border of the game
    top_border = board["height"]-1
    bottom_border = 0
    right_border = board["width"]-1
    left_border = 0

    head = snake["body"][0]

    safe_moves = {"up": True, "down": True, "left": True, "right": True}

    # walls
    if head["y"] == top_border:
        safe_moves["up"] = False
    if head["y"] == bottom_border:
        safe_moves["down"] = False
    if  head["x"] == right_border:
        safe_moves["right"] = False
    if head["x"] == left_border:
        safe_moves["left"] = False

    # Snake Body
    for body in snake["body"]:
        if body == head:
            continue

        if head["y"] == body["y"]:
            if head["x"]+1 == body["x"]:
                safe_moves["right"] = False
            if head["x"]-1 == body["x"]:
                safe_moves["left"] = False
        if head["x"] == body["x"]:
            if head["y"]+1 == body["y"]:
                safe_moves["up"] = False
            if head["y"]-1 == body["y"]:
                safe_moves["down"] = False

    # Opponents
    opponents = state['board']['snakes']

    for opponent in opponents:
        if opponent == ['you']:
            continue

        for enemy_body in opponent['body']:
            if head["y"] == enemy_body["y"]:
                if head["x"] + 1 == enemy_body["x"]:
                    safe_moves["right"] = False
                if head["x"] - 1 == enemy_body["x"]:
                    safe_moves["left"] = False
            if head["x"] == enemy_body["x"]:
                if head["y"] + 1 == enemy_body["y"]:
                    safe_moves["up"] = False
                if head["y"] - 1 == enemy_body["y"]:
                    safe_moves["down"] = False

    return safe_moves

def make_training_example(game_state, direction, *, label_source, seed=None):
    """Build an independent state/action snapshot for any agent's dataset.

    The caller owns the rows and decides when to store them. For example:
    rows.append(make_training_example(state, direction, label_source="my_agent"))
    """
    row = {
        **state_to_attributes(game_state),
        "game_id": game_state["game"]["id"],
        "turn": game_state["turn"],
        "seed": seed,
        "direction": direction,
        "label_source": label_source,
        "state": game_state,
    }
    return copy.deepcopy(row)


def load_dataframe(path):
    """Restore the saved pandas DataFrame, including its nested apple lists."""
    df = pd.read_json(Path(path), orient="table")
    required = set(INPUT_COLUMNS + ["game_id", "turn", "direction", "state"])
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}. Record a new dataset after changing attributes.")
    if df.empty:
        raise ValueError("The DataFrame is empty. Record some agent decisions in Step 1 first.")
    if not df["direction"].isin(ACTIONS).all():
        raise ValueError("Every label must be up, down, left or right.")
    if df.duplicated(["game_id", "turn"]).any():
        raise ValueError("The dataset contains duplicate game/turn pairs.")
    return df
