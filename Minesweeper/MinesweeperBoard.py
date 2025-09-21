"""
Module: MinesweeperBoard
Class: Minesweeper
Description: Defines the Minesweeper game board and logic for placing mines,
                revealing squares, toggling flags, and end conditions.
Inputs: Width, height, and number of mines defining the initial board setup.
Outputs: Minesweeper game board.
External Sources: None
Authors: Kiara [Sam] Grimsley, Reeny Huang, Lauren D'Souza, Audrey Pan, Ella Nguyen, Hart Nurnberg
Created: September 19, 2025 (original prototype August 25, 2025)
Last Modified: September 19, 2025
"""

import random

class Minesweeper:
    def __init__(self, width, height, num_mines):
        """Take a width, height, and mine number to create a Minesweeper game board."""
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.flags_remaining = num_mines
        self.board = [[0 for _ in range(width)] for _ in range(height)]
        self.revealed = [[False for _ in range(width)] for _ in range(height)]
        self.flags = [[False for _ in range(width)] for _ in range(height)]
        self.game_over = False
        self.mines_placed = False  # Flag to track if mines have been placed

    def place_mines(self, safe_x=None, safe_y=None):
        """Place mines, ensuring the first square is safe."""
        mines = 0
        while mines < self.num_mines:
            # Random position, make sure valid placement
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            if self.board[y][x] != -1 and not (x == safe_x and y == safe_y):
                self.board[y][x] = -1
                mines += 1

    def calculate_square(self, x, y):
        """Calculate the number of adjacent mines for a given square."""
        if self.board[y][x] == -1: # Mines don't need calculation
            return
        adj = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                # If not out of bounds
                if 0 <= x + i < self.width and 0 <= y + j < self.height:
                    # If adjacent mine then ++
                    if self.board[y + j][x + i] == -1:
                        adj += 1
        self.board[y][x] = adj

    def calculate_squares(self):
        """Calculate the number of adjacent mines for all squares."""
        for y in range(self.height):
            for x in range(self.width):
                self.calculate_square(x, y)

    def reveal_square(self, x, y):
        """Reveal a square on the board. If 0 square, reveal adjacent squares."""
        if self.revealed[y][x] or self.flags[y][x] or self.game_over:
            return

        # Place mines after first click, ensuring the first square is safe
        if not self.mines_placed:
            self.place_mines(safe_x=x, safe_y=y)
            self.calculate_squares()
            self.mines_placed = True

        self.revealed[y][x] = True

        # Mine then lose
        if self.board[y][x] == -1:
            self.reveal_all_mines()
            self.game_over = True
            return

        # If the square is empty (0), reveal adjacent squares
        if self.board[y][x] == 0:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if 0 <= x + i < self.width and 0 <= y + j < self.height:
                        self.reveal_square(x + i, y + j)

    def toggle_flag(self, x, y):
        """Toggle a flag on a square if flaggable."""
        if self.revealed[y][x] or self.game_over:
            return

        flag_status = not self.flags[y][x]
        self.flags[y][x] = flag_status

        self.flags_remaining += -1 if flag_status else 1

    def is_game_over(self):
        """True if loss, false otherwise."""
        return self.game_over

    def is_game_won(self):
        """True if all non-mine squares are revealed, false otherwise."""
        return all(self.revealed[y][x] or self.board[y][x] == -1 for y in range(self.height) for x in range(self.width))

    def get_display_board(self):
        """Returns the current state of the board for display purposes."""
        display_board = [[] for _ in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                if self.revealed[y][x]:
                    display_board[y].append(self.board[y][x]) # Revealed, number or mine
                elif self.flags[y][x]:
                    display_board[y].append("F") # Flagged
                else:
                    display_board[y].append("?") # Hidden
        return display_board

    #iterates through the board and reveals all squares with mines
    def reveal_all_mines(self):
        """Reveal all mines on the board."""
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == -1:
                    self.revealed[y][x] = True


