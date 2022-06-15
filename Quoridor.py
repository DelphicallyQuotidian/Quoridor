# Description: Allows two players to play Quoridor. Each player can either move their pawn or place a fence on their
# turn. The players begin with 10 fence pieces, and with their pieces at Player1 = (4, 0) and Player2 = (4, 8).
# The board is a 9 x 9 grid, with the outer edges being considered fences. The goal is for the player's pawn to reach
# the row at the other side of the board.


class QuoridorGame:
    """
    Controls interactions with the Quoridor game
    """
    def __init__(self):
        """
        Initializes the game with a Board, whose turn it is (Player 1), whether the game is over (0 = False), and how
        many fences each player begins with (10)
        """
        self._board = Board()
        self._player_turn = 1  # 1 for Player 1, 2 for Player 2
        self._game_over = 0  # 0 when game in progress, 1 if Player 1 wins, 2 if Player 2 wins
        self._player_1_fences = 10
        self._player_2_fences = 10

    def move_pawn(self, player, new_pos):
        """
        Moves the pawn of player 1 or player 2 (player) to the new position they selected (new_pos).
        Parameters: player: the player making a move (integer value of 1 or 2), new_pos: a tuple (x-coord, y-coord)
        describing the position the player wants to move their piece to.
        Return: False if the game has already been won, the wrong player is moving, the move is invalid; True if move
        was completed as specified.
        """
        # Check whether game already won
        if self._game_over:
            return False
        # Check whether valid player is moving their pawn
        if player != self._player_turn:
            return False
        # Move pawn - calls Board's move_pawn (which checks whether the move itself is valid)
        if self._board.move_pawn(player, new_pos):  # if makes the move successfully
            if self._board.player_in_goal(player):  # tests whether the player won and updates game state if did
                self._game_over = player
            # update which player's turn it is
            if player == 1:
                self._player_turn = 2
            else:
                self._player_turn = 1
            return True
        return False

    def place_fence(self, player, direction, position):
        """
        Places a fence for player 1 or player 2 (player) at the indicated position (position)
        in the indicated direction (direction).
        Parameters: player: the player placing a fence (integer 1 or 2), direction: the direction the fence is oriented
        ("v" = vertical or "h" = horizontal), position: a tuple (x-coord, y-coord) representing where the fence is to
        be placed (the upper left corner of a square)
        Return: False if the game was over, it wasn't player's turn, or the player doesn't have fence pieces; True if
        the fence was placed successfully
        """
        # Check whether game already won
        if self._game_over:
            return False
        # Check whether valid player is moving their pawn
        if player != self._player_turn:
            return False
        # Check whether player has fence pieces
        if player == 1 and self._player_1_fences == 0:
            return False
        elif player == 2 and self._player_2_fences == 0:
            return False
        # Try to place the piece
        piece_placed = self._board.place_fence(direction, position)
        if piece_placed == "breaks the fair play rule":
            return "breaks the fair play rule"
        elif piece_placed:
            # update which player's turn it is
            if player == 1:
                self._player_turn = 2
                self._player_1_fences -= 1
            else:
                self._player_turn = 1
                self._player_2_fences -= 1
            return True
        return False

    def is_winner(self, player):
        """
        Takes a player (integer 1 or 2) and returns True if that player has won, False otherwise
        """
        if self._game_over == player:
            return True
        return False

    def print_board(self):
        """
        Prints the current state of the board.
        *Intended for debugging use only.
        """
        print(self._board)


class Board:
    """
    Represents the Quoridor game board.
    Stores the current state of the game board (fence placement and player piece locations)
    """
    def __init__(self):
        """
        Initializes the locations of player 1 and player 2 (tuples) and generates the board
        """
        # Set player locations
        self._player_1 = (4, 0)
        self._player_2 = (4, 8)
        # Generate the board
        self._board = []
        for row in range(0, 9):
            new_row = []
            for col in range(0, 9):
                tile = Tile()
                tile.set_board_coord((col, row))
                new_row.append(tile)
            self._board.append(new_row)
        # Open the connecting Tiles without fences
        for tile_row in range(0, 9):
            for tile_col in range(0, 9):
                if tile_col != 0:
                    self._board[tile_row][tile_col].open_direction("west", self._board[tile_row][tile_col -1])
                if tile_col != 8:
                    self._board[tile_row][tile_col].open_direction("east", self._board[tile_row][tile_col + 1])
                if tile_row != 0:
                    self._board[tile_row][tile_col].open_direction("north", self._board[tile_row - 1][tile_col])
                if tile_row != 8:
                    self._board[tile_row][tile_col].open_direction("south", self._board[tile_row + 1][tile_col])
        # place player on the board
        self._board[0][4].set_has_pawn(1)
        self._board[8][4].set_has_pawn(2)

    def get_player_1(self):
        """Returns player 1's location (tuple)"""
        return self._player_1

    def get_player_2(self):
        """Returns player 2's location (tuple)"""
        return self._player_2

    def player_in_goal(self, player):
        """
        Parameters: player (integer 1 or 2)
        Returns: True if player reaches their victory zone, False otherwise
        """
        if player == 1 and self._player_1[1] == 8:
            return True
        elif player == 2 and self._player_2[1] == 0:
            return True
        return False

    def _can_jump_pawn(self, current_tile, row_dir, col_dir):
        """
        Tests whether the player is moving two tiles horizontally or vertically by legally jumping over the opponent's
        pawn. There cannot be fences between any of the tiles.
        Parameters: current_tile (Tile player occupies), row_dir (number of tiles player will move north or south),
        col_dir (number of tiles player will move east or west)
        Return: True if can legally jump opponent's pawn, False if not
        """
        if (abs(row_dir) == 2 or abs(col_dir) == 2) and (abs(row_dir) == 0 or abs(col_dir) == 0):
            next_tile = current_tile.get_direction((col_dir, row_dir))
            if next_tile is not None and next_tile.get_has_pawn() != 0:  # pawn blocking path and no fence
                if next_tile.get_direction((col_dir, row_dir)) is not None:  # no fence behind pawn in way
                    return True
        return False

    def _can_move_diagonally(self, current_tile, row_dir, col_dir):
        """
        Tests whether the player is moving a single tile diagonally, which is only legal when the player is blocked
        by the opponent piece and there is also a fence behind the opponent.
        Parameters: current_tile (Tile player occupies), row_dir (number of tiles player will move north or south),
        col_dir (number of tiles player will move east or west)
        Return: True if can legally move diagonally, False if not
        """
        if abs(row_dir) == 1 and abs(col_dir) == 1:
            change_col = current_tile.get_direction((col_dir, 0))
            change_row = current_tile.get_direction((0, row_dir))
            if change_col is not None and change_col.get_has_pawn():  # enemy pawn is in an adjacent column
                # ensure that there is a wall behind opponent's pawn and there is not a wall blocking the diagonal move
                if change_col.get_direction((col_dir, 0)) is None and change_col.get_direction((0, row_dir)) is not None:
                    return True
                return False
            elif change_row is not None and change_row.get_has_pawn():  # enemy pawn is in an adjacent row
                # ensure that there is a wall behind opponent's pawn and there is not a wall blocking the diagonal move
                if change_row.get_direction((0, row_dir)) is None and change_row.get_direction((col_dir, 0)) is not None:
                    return True
                return False
        return False

    def _can_move_regularly(self, current_tile, row_dir, col_dir):
        """
        Tests whether the player is moving a single tile horizontally or vertically and ensures that there is no fence
        between the player and their desired open tile.
        Parameters: current_tile (Tile player occupies), row_dir (number of tiles player will move north or south),
        col_dir (number of tiles player will move east or west)
        Return: True if can legally move horizontally/vertically, False otherwise
        """
        if (abs(row_dir) == 1 or abs(col_dir) == 1) and (abs(row_dir) == 0 or abs(col_dir) == 0):
            if current_tile.get_direction((col_dir, row_dir)) is not None:  # no wall
                return True
        return False

    def move_pawn(self, player, new_pos):
        """
        Handles the validity checks for whether player can move to new_pos, and moves the player to the new location if
        legal.
        Parameters: player (integer 1 or 2) and new_pos (a tuple of the coordinates to move to (x-coord, y-coord)
        Returns: True if player completes their move successfully, False otherwise.
        """
        # Check whether new position is in-bounds and unoccupied
        if not (0 <= new_pos[0] <= 8) or not (0 <= new_pos[1] <= 8):  # not out-of-bounds
            return False
        new_tile = self._board[new_pos[1]][new_pos[0]]
        if new_tile.get_has_pawn():  # has a player in that position
            return False

        # get player's current position
        if player == 1:
            current_pos = self._player_1
        else:
            current_pos = self._player_2
        current_tile = self._board[current_pos[1]][current_pos[0]]
        # calculate which direction and how far the player is trying to move
        row_dir, col_dir = new_pos[1] - current_pos[1], new_pos[0] - current_pos[0]

        # check whether player is moving horizontally/vertically/diagonally in a legal manner
        moving_regularly = self._can_move_regularly(current_tile, row_dir, col_dir)
        jumping_pawn = self._can_jump_pawn(current_tile, row_dir, col_dir)
        moving_diagonally = self._can_move_diagonally(current_tile, row_dir, col_dir)
        if moving_regularly or jumping_pawn or moving_diagonally:
            current_tile.set_has_pawn(0)  # pawn no longer occupies this Tile
            new_tile.set_has_pawn(player)  # pawn now occupies this Tile
            if player == 1:
                self._player_1 = new_pos
            else:
                self._player_2 = new_pos
            return True
        return False

    def _fair_play(self, player):
        """
        Finds a path from player 1 to player 1's goal and from player 2 to player 2's goal. If either player doesn't
        have a valid path to their goal, returns False. Only tests whether fences are blocking the player's path, NOT
        whether the enemy player is in the way.
        Parameter: player (integer 1 or 2)
        Returns: True if both players can still reach their goals, False otherwise
        """
        if player == 1:
            destination = 8
            position = self.get_player_1()
        else:
            destination = 0
            position = self.get_player_2()
        tile = self._board[position[1]][position[0]]  # starting Tile
        paths = tile.get_valid_directions()  # list of path directions
        paths_taken = {position}  # a set to track which Tiles have been visited
        for path in paths:
            paths_taken.add(path)
        while len(paths) > 0:
            if paths[0].get_board_coord()[1] == destination:
                return True
            new_paths = paths[0].get_valid_directions()
            for new_path in new_paths:
                if new_path not in paths_taken:
                    paths.append(new_path)
                    paths_taken.add(new_path)
            paths.pop(0)
        return False

    def _place_fence_in_direction(self, direction, tile):
        """
        Handles placing the fence either vertically or horizontally for place_fence, and ensures that the move is
        valid and does not violate the fair play rules.
        Parameters: direction ("v" or "h"), tile (a Tile object)
        Returns: True if the fence is successfully placed, "breaks the fair play rule" if the position breaks the fair
        play rule, False otherwise
        """
        if direction == "v":
            border_tile = tile.get_direction((-1, 0))
            if border_tile is None:  # make sure no fence already exists
                return False
            tile.close_direction("west")
            border_tile.close_direction("east")
            # make sure the fence doesn't prevent a player from winning
            if not self._fair_play(1) or not self._fair_play(2):
                tile.open_direction("west", border_tile)
                border_tile.open_direction("east", tile)
                return "breaks the fair play rule"
        elif direction == "h":
            border_tile = tile.get_direction((0, -1))
            if border_tile is None:  # make sure no fence already exists
                return False
            tile.close_direction("north")
            border_tile.close_direction("south")
            # make sure the fence doesn't prevent a player from winning
            if not self._fair_play(1) or not self._fair_play(2):
                tile.open_direction("north", border_tile)
                border_tile.open_direction("south", tile)
                return "breaks the fair play rule"
        return True

    def place_fence(self, direction, position):
        """
        Tests whether the fence position is valid, then places the fence on the board if it is.
        Parameters: direction ("v" or "h"), position (tuple representing where to place the fence (x-coord, y-coord))
        Returns: True if fence placed, "breaks the fair play rule" if breaks the fair play rule, otherwise False
        """
        # Check whether placing in a valid direction (v, h)
        if not (direction == "v" or direction == "h"):
            return False
        # make sure fence is on the board
        if not (0 <= position[0] <= 8) or not (0 <= position[1] <= 8):
            return False
        tile = self._board[position[1]][position[0]]
        # runs the remaining tests for validity and fair play, then places the fence piece if valid
        return self._place_fence_in_direction(direction, tile)

    def __repr__(self):
        """Displays the board for debugging purposes"""
        board_str = ""
        for row in range(0, 9):
            row_str = ""
            below_str = ""
            north_str = ""
            for col in range(0, 9):
                tile = self._board[row][col]
                if tile.get_direction((0, -1)):
                    north_str += "   "
                else:
                    north_str += " - "
                if tile.get_direction((-1, 0)):
                    row_str += " "
                else:
                    row_str += "|"
                row_str += str(tile.get_has_pawn())
                if tile.get_direction((1, 0)):
                    row_str += " "
                else:
                    row_str += "|"
                if tile.get_direction((0, 1)):
                    below_str += "   "
                else:
                    below_str += " - "
            board_str += north_str + "\n" + row_str + "\n" + below_str + "\n"
        return board_str


class Tile:
    """
    Represents a position on the board that the pawn can occupy.
    Stores fences in north, south, east, west. Stores pawn placement with has_pawn. Stores its own coordinates on Board.
    """
    def __init__(self):
        """
        Initializes the Tile with positions that fences can occupy (north, south, east, west) and whether the pawn
        is currently occupying that position (has_pawn).
        """
        self._north = None  # points to the Tile to the north, None if closed (has a fence)
        self._south = None
        self._east = None
        self._west = None
        self._has_pawn = 0  # 0 for no pawn, 1 for player 1, 2 for player 2
        self._board_coord = None

    def get_direction(self, movement):
        """
        Takes a tuple with the number of spaces the player is moving on the x- and y- coordinates.
        Returns the function to get the tile in that direction (get_north, etc.).
        """
        # x-axis (columns)
        if movement[0] < 0:
            return self._west
        if movement[0] > 0:
            return self._east
        # y-axis (rows)
        if movement[1] < 0:
            return self._north
        if movement[1] > 0:
            return self._south

    def get_valid_directions(self):
        """Returns a list of the connecting Tiles in all directions (north/south/east/west)"""
        tiles = []
        if self._north is not None:
            tiles.append(self._north)
        if self._south is not None:
            tiles.append(self._south)
        if self._east is not None:
            tiles.append(self._east)
        if self._west is not None:
            tiles.append(self._west)
        return tiles

    def get_has_pawn(self):
        """Returns 0 for no pawn, 1 for player 1's pawn, 2 for player 2's pawn"""
        return self._has_pawn

    def get_board_coord(self):
        """Returns the Tile's coordinates on the Board as a tuple (x-coord, y-coord)"""
        return self._board_coord

    def close_direction(self, direction):
        """
        Represents placing a fence to the direction of the tile - changes to None
        """
        if direction == "north":
            self._north = None
        elif direction == "south":
            self._south = None
        elif direction == "west":
            self._west = None
        elif direction == "east":
            self._east = None

    def open_direction(self, direction, tile):
        """
        Takes a direction (string - north, south, east, west) and sets that direction to point to tile (a Tile).
        """
        if direction == "north":
            self._north = tile
        elif direction == "south":
            self._south = tile
        elif direction == "west":
            self._west = tile
        elif direction == "east":
            self._east = tile

    def set_has_pawn(self, pawn):
        """
        Takes an integer in range [0, 2] and sets has_pawn to that value (0 for no pawn, 1 for player 1, 2 for player 2)
        """
        self._has_pawn = pawn

    def set_board_coord(self, coords):
        """
        Sets new coordinates for the Tile
        Parameter: coords - tuple of (x-coord, y-coord) on the Board
        """
        self._board_coord = coords


def main():
    """Runs when Quoridor.py is run as a script"""
    pass


if __name__ == "__main__":
    main()
