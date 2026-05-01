"""Unit tests for Sokoban game logic."""

import pytest
from game import Direction, GameState, parse_level

UP = Direction.UP
DOWN = Direction.DOWN
LEFT = Direction.LEFT
RIGHT = Direction.RIGHT


def lvl(lines):
    """Shorthand: parse a list of strings into a GameState."""
    return parse_level(lines)


# ── fixtures (small hand-crafted boards) ─────────────────────────────────────
#
# Coordinate reference: row 0 is the top line, col 0 is the leftmost char.
# Board key:  # wall   @ player   $ box   . target   * box-on-target
#             + player-on-target   (space) floor

OPEN = [         # player can move in all four directions
    "#####",
    "# @ #",
    "#   #",
    "#####",
]

TRAPPED = [      # player is completely walled in
    "#####",
    "##@##",
    "#####",
]

WALL_RIGHT = [   # wall immediately to the right of player
    "####",
    "#@##",
    "####",
]

WALL_DOWN = [    # wall immediately below
    "###",
    "#@#",
    "###",
]

BOX_OPEN = [     # box with empty space behind it (pushable right)
    "######",
    "#@$  #",
    "######",
]

BOX_INTO_WALL = [    # box with wall immediately behind it (right push blocked)
    "#####",
    "#@$##",
    "#####",
]

BOX_WALL_DOWN = [    # box with wall below (down push blocked)
    "###",
    "#@#",
    "#$#",
    "###",
]

BOX_INTO_BOX = [     # two boxes in a row (can't push right)
    "######",
    "#@$$ #",
    "######",
]

BOX_INTO_BOX_VERT = [  # two boxes stacked vertically (can't push down)
    "###",
    "#@#",
    "#$#",
    "#$#",
    "###",
]

SIMPLE_WIN = [       # one move wins: push box right onto target
    "#####",
    "#@$.#",
    "#####",
]

TWO_BOX_WIN = [      # two boxes, two targets; one push is not enough to win
    "########",
    "#@$ $..#",
    "########",
]

ON_TARGET_START = [  # player starts on a target
    "#####",
    "#.@.#",
    "#$  #",
    "#####",
]

BOX_STARTS_ON_TARGET = [  # box already on target at parse time
    "#####",
    "#@*.#",
    "#####",
]

UNDO_BOARD = [
    "#######",
    "#@$   #",
    "#  .  #",
    "#######",
]


# ── parse_level ───────────────────────────────────────────────────────────────

class TestParseLevel:
    def test_player_position(self):
        gs = lvl(["###", "#@#", "###"])
        assert gs.player == (1, 1)

    def test_box_detected(self):
        gs = lvl(BOX_OPEN)
        assert (1, 2) in gs.boxes

    def test_target_detected(self):
        gs = lvl(SIMPLE_WIN)
        assert (1, 3) in gs.targets

    def test_box_on_target_in_both_sets(self):
        gs = lvl(BOX_STARTS_ON_TARGET)
        assert (1, 2) in gs.boxes
        assert (1, 2) in gs.targets

    def test_player_on_target_parsed(self):
        gs = lvl(["###", "#.+#", "###"])
        assert gs.player == (1, 2)
        assert (1, 2) in gs.targets
        assert (1, 2) not in gs.boxes

    def test_grid_padded_to_uniform_width(self):
        gs = lvl(["#####", "# @ #", "###"])  # last row shorter
        assert all(len(row) == 5 for row in gs.grid)

    def test_missing_player_raises(self):
        with pytest.raises(ValueError):
            lvl(["###", "# #", "###"])

    def test_rows_and_cols(self):
        gs = lvl(OPEN)
        assert gs.rows == 4
        assert gs.cols == 5


# ── can_move / basic movement ────────────────────────────────────────────────

class TestBasicMovement:
    def test_move_right_into_floor(self):
        gs = lvl(OPEN)   # player at (1,2)
        assert gs.can_move(RIGHT)

    def test_move_left_into_floor(self):
        gs = lvl(OPEN)
        assert gs.can_move(LEFT)

    def test_move_up_blocked_by_wall(self):
        gs = lvl(OPEN)   # row 0 is wall
        assert not gs.can_move(UP)

    def test_move_all_blocked_when_trapped(self):
        gs = lvl(TRAPPED)
        for d in Direction:
            assert not gs.can_move(d)

    def test_move_right_blocked_by_wall(self):
        gs = lvl(WALL_RIGHT)   # player at (1,1), wall at (1,2)
        assert not gs.can_move(RIGHT)

    def test_move_down_blocked_by_wall(self):
        gs = lvl(WALL_DOWN)    # player at (1,1), wall at (2,1)
        assert not gs.can_move(DOWN)

    def test_move_updates_player_position(self):
        gs = lvl(OPEN)   # player at (1,2)
        gs.move(RIGHT)
        assert gs.player == (1, 3)

    def test_move_increments_move_counter(self):
        gs = lvl(OPEN)
        assert gs.moves == 0
        gs.move(RIGHT)
        assert gs.moves == 1

    def test_failed_move_does_not_increment_counter(self):
        gs = lvl(TRAPPED)
        gs.move(UP)
        assert gs.moves == 0

    def test_move_returns_true_on_success(self):
        gs = lvl(OPEN)
        assert gs.move(RIGHT) is True

    def test_move_returns_false_on_failure(self):
        gs = lvl(TRAPPED)
        assert gs.move(RIGHT) is False


# ── box pushing ───────────────────────────────────────────────────────────────

class TestBoxPushing:
    def test_can_push_box_into_empty_space(self):
        gs = lvl(BOX_OPEN)   # player (1,1), box (1,2), floor (1,3)
        assert gs.can_move(RIGHT)

    def test_cannot_push_box_into_wall(self):
        gs = lvl(BOX_INTO_WALL)   # box at (1,2), wall at (1,3)
        assert not gs.can_move(RIGHT)

    def test_cannot_push_box_into_another_box(self):
        gs = lvl(BOX_INTO_BOX)   # boxes at (1,2) and (1,3)
        assert not gs.can_move(RIGHT)

    def test_cannot_push_two_boxes_vertically(self):
        gs = lvl(BOX_INTO_BOX_VERT)
        assert not gs.can_move(DOWN)

    def test_cannot_push_box_down_into_wall(self):
        gs = lvl(BOX_WALL_DOWN)
        assert not gs.can_move(DOWN)

    def test_push_moves_box_to_new_position(self):
        gs = lvl(BOX_OPEN)   # box starts at (1,2)
        gs.move(RIGHT)
        assert (1, 3) in gs.boxes
        assert (1, 2) not in gs.boxes

    def test_push_increments_push_counter(self):
        gs = lvl(BOX_OPEN)
        gs.move(RIGHT)
        assert gs.pushes == 1

    def test_regular_move_does_not_increment_pushes(self):
        gs = lvl(OPEN)
        gs.move(RIGHT)
        assert gs.pushes == 0

    def test_box_pushed_left(self):
        gs = lvl(["######", "#  $@#", "######"])  # player (1,4), box (1,3)
        gs.move(LEFT)
        assert (1, 2) in gs.boxes
        assert (1, 3) not in gs.boxes

    def test_box_pushed_up(self):
        gs = lvl(["###", "# #", "#$#", "#@#", "###"])
        gs.move(UP)
        assert (1, 1) in gs.boxes
        assert (2, 1) not in gs.boxes

    def test_box_pushed_down(self):
        gs = lvl(["###", "#@#", "#$#", "# #", "###"])
        gs.move(DOWN)
        assert (3, 1) in gs.boxes
        assert (2, 1) not in gs.boxes


# ── completion ────────────────────────────────────────────────────────────────

class TestCompletion:
    def test_not_complete_at_start(self):
        gs = lvl(SIMPLE_WIN)
        assert not gs.is_complete()

    def test_complete_after_pushing_box_onto_target(self):
        gs = lvl(SIMPLE_WIN)   # push box right: (1,2)→(1,3) which is target
        gs.move(RIGHT)
        assert gs.is_complete()

    def test_complete_only_when_all_boxes_on_targets(self):
        # TWO_BOX_WIN: player (1,1), boxes (1,2) and (1,4), targets (1,5) and (1,6)
        gs = lvl(TWO_BOX_WIN)
        gs.move(RIGHT)   # pushes box (1,2)→(1,3); second box untouched
        assert not gs.is_complete()

    def test_spare_goals_do_not_block_completion(self):
        # Win condition: ALL crates on a goal — spare goals are irrelevant.
        # BOX_STARTS_ON_TARGET has 1 box on (1,2) and 2 targets: (1,2) and (1,3).
        gs = lvl(BOX_STARTS_ON_TARGET)
        assert gs.is_complete()

    def test_all_boxes_already_on_targets_is_complete(self):
        gs = lvl(["#####", "#@* #", "#####"])   # one box on only target
        assert gs.is_complete()


# ── undo ──────────────────────────────────────────────────────────────────────

class TestUndo:
    def test_undo_restores_player_position(self):
        gs = lvl(OPEN)
        gs.move(RIGHT)
        assert gs.player == (1, 3)
        gs.undo()
        assert gs.player == (1, 2)

    def test_undo_restores_box_position(self):
        gs = lvl(UNDO_BOARD)   # player (1,1), box (1,2)
        gs.move(RIGHT)
        assert (1, 3) in gs.boxes
        gs.undo()
        assert (1, 2) in gs.boxes
        assert (1, 3) not in gs.boxes

    def test_undo_decrements_move_counter(self):
        gs = lvl(OPEN)
        gs.move(RIGHT)
        gs.undo()
        assert gs.moves == 0

    def test_undo_decrements_push_counter(self):
        gs = lvl(UNDO_BOARD)
        gs.move(RIGHT)
        assert gs.pushes == 1
        gs.undo()
        assert gs.pushes == 0

    def test_undo_when_empty_returns_false(self):
        gs = lvl(OPEN)
        assert gs.undo() is False

    def test_multi_step_undo(self):
        gs = lvl(OPEN)
        gs.move(RIGHT)
        gs.move(DOWN)
        gs.undo()
        gs.undo()
        assert gs.player == (1, 2)
        assert gs.moves == 0

    def test_undo_does_not_undo_failed_move(self):
        gs = lvl(TRAPPED)
        gs.move(RIGHT)   # fails, nothing added to history
        assert gs.undo() is False


# ── display_char ──────────────────────────────────────────────────────────────

class TestDisplayChar:
    def test_wall_renders_as_hash(self):
        gs = lvl(OPEN)
        assert gs.display_char(0, 0) == "#"

    def test_floor_renders_as_space(self):
        gs = lvl(OPEN)
        assert gs.display_char(1, 1) == " "

    def test_player_renders_at_position(self):
        gs = lvl(OPEN)  # player at (1,2)
        assert gs.display_char(1, 2) == "@"

    def test_box_renders_as_dollar(self):
        gs = lvl(BOX_OPEN)
        assert gs.display_char(1, 2) == "$"

    def test_target_renders_as_dot(self):
        gs = lvl(SIMPLE_WIN)
        assert gs.display_char(1, 3) == "."

    def test_box_on_target_renders_as_star(self):
        gs = lvl(BOX_STARTS_ON_TARGET)
        assert gs.display_char(1, 2) == "*"

    def test_player_on_target_renders_as_plus(self):
        gs = lvl(ON_TARGET_START)  # player at (1,2), target at (1,1) and (1,3)
        # Move player left onto target at (1,1)
        gs.move(LEFT)
        assert gs.display_char(1, 1) == "+"


# ── pathfinding (find_path) ───────────────────────────────────────────────────

class TestFindPath:
    def test_path_to_adjacent_cell(self):
        gs = lvl(OPEN)   # player at (1,2)
        path = gs.find_path((1, 3))
        assert path == [RIGHT]

    def test_path_to_self_is_empty(self):
        gs = lvl(OPEN)
        assert gs.find_path(gs.player) == []

    def test_no_path_through_wall(self):
        gs = lvl(OPEN)
        assert gs.find_path((0, 0)) is None   # (0,0) is a wall

    def test_no_path_through_box(self):
        gs = lvl(BOX_OPEN)   # player (1,1), box (1,2)
        # (1,3) is blocked by box at (1,2)
        assert gs.find_path((1, 3)) is None

    def test_path_routes_around_box(self):
        board = [
            "#######",
            "#@$   #",
            "#     #",
            "#######",
        ]
        gs = lvl(board)  # player (1,1), box (1,2)
        # Target (1,4) is unreachable directly (box at 1,2 blocks the row)
        # but reachable via row 2
        path = gs.find_path((1, 4))
        assert path is not None
        assert len(path) > 0

    def test_multi_step_path(self):
        gs = lvl(OPEN)   # player at (1,2)
        path = gs.find_path((2, 2))   # one step down
        assert path is not None
        assert DOWN in path
