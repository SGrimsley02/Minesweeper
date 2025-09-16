"""
TODO: Prologue comment placeholder
    Due to grading criteria we probably need to split this into two files
    To avoid merge conflicts with existing branches, I'm waiting until
    later to do this -Kiara
"""

import pygame as pg
import pygame_textinput as textinput
import random

# Board layout (fixed 10x10)
BOARD_WIDTH = 10
BOARD_HEIGHT = 10

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRID_LINE = (255, 255, 255)
HIDDEN = (247, 225, 215)
REVEALED_EMPTY = (222, 219, 210)
REVEALED_NUMBER = (176, 196, 177)
MINE_RED = (219, 110, 110)
BACKGROUND = (74, 87, 89)
GENERAL_TEXT = (176, 196, 177)
TRANSPARENT_RED = (255, 155, 155, 180)
TRANSPARENT_GREEN = (155, 255, 155, 200)

# Minesweeper prototype
class Minesweeper:
    def __init__(self, width, height, num_mines):
        """Take a width, height, and mine number to create a Minesweeper game."""
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
                    display_board[y].append(self.board[y][x])
                elif self.flags[y][x]:
                    display_board[y].append("F")
                else:
                    display_board[y].append("?")
        return display_board
    
    #iterates through the board and reveals all squares with mines
    def reveal_all_mines(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x] == -1:
                    self.revealed[y][x] = True

class Game:
    def __init__(self):
        """Initialize the game."""
        self.minesweeper = None
        self.quit = False
        pg.init()

    def start_game(self, width: int, height: int, num_mines: int):
        """Start a new minesweeper board with given width, height, and num_mines."""
        self.minesweeper = Minesweeper(width, height, num_mines)

    def exit_game(self):
        """Perform any game cleanup here (if needed), then quit()."""
        pg.quit()

    def play_minesweeper():
        """Static method to play Minesweeper."""
        game = Game()
        game.run()
        
    def mouse_to_grid(self, mx: int, my: int, grid_x0, grid_y0, cell_size, grid_width, grid_height):
        """Convert mouse pixel coordinates (mx, my) to grid coordinates (gx, gy), or None if click outside of board"""
        if not (grid_x0 <= mx < grid_x0 + cell_size * grid_width and grid_y0 <= my < grid_y0 + cell_size * grid_height):
            return None
        gx = (mx - grid_x0) // cell_size
        gy = (my - grid_y0) // cell_size
        return int(gx), int(gy)

    def run(self):
        """Main game loop. Title screen followed by game."""
        screen = pg.display.set_mode((600, 600), pg.RESIZABLE)
        clock = pg.time.Clock()
        font = pg.font.SysFont(None, 24)

        # Cap mines at 20 as per requirements
        mines_input = textinput.TextInputVisualizer(manager=textinput.TextInputManager(validator=lambda x: (x.isdigit() and int(x) <= 20) or x == ''),
                                                    font_color=GENERAL_TEXT,
                                                    cursor_color=WHITE
                                                    )

        # Title screen loop
        while not self.minesweeper and not self.quit:
            screen.fill(BACKGROUND)
            pg.display.set_caption("Minesweeper")

            w, h = screen.get_size()
            grid_size = min(w, h) * 0.8
            cell_size = int(grid_size // BOARD_WIDTH)
            grid_width = BOARD_WIDTH * cell_size
            grid_height = BOARD_HEIGHT * cell_size
            grid_x0 = (w - grid_width) // 2
            grid_y0 = (h - grid_height) // 2

            # Render text centered above grid
            mines_text = font.render("Enter Mine Count (10-20): ", True, GENERAL_TEXT)
            mines_text_y = max(10, grid_y0 - 40)
            mines_text_rect = mines_text.get_rect(center=(w // 2, mines_text_y))
            screen.blit(mines_text, mines_text_rect)

            events = pg.event.get()

            # Updates mine and render mine-count input field
            mines_input.update(events)
            mines_input_rect = mines_input.surface.get_rect(center=(w // 2, grid_y0 + grid_height // 2))
            screen.blit(mines_input.surface, mines_input_rect)

            # Draw hint text
            hint_text = font.render("Press Enter to Start", True, (GENERAL_TEXT))
            hint_text_y = min(h - 10, grid_y0 + grid_height + 10)
            hint_text_x = max(w // 2, min(w - w // 2, w // 2))
            hint_text_rect = hint_text.get_rect(center=(hint_text_x, hint_text_y))
            screen.blit(hint_text, hint_text_rect)

            # Handle key presses
            for event in events:
                if event.type == pg.QUIT:
                    self.quit = True
                    break
                if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    # Start game if mine count provided and within 10-20 range
                    if (mines_input.value and 10 <= int(mines_input.value) <= 20):
                        num_mines = int(mines_input.value)
                        self.start_game(BOARD_WIDTH, BOARD_HEIGHT, num_mines)

            pg.display.update()
            clock.tick(60)

        while not self.quit:  # Main game loop
            pg.display.set_caption("Minesweeper -- Game")
            w, h = screen.get_size()
            grid_size = min(w, h) * 0.8
            cell_size = int(grid_size // BOARD_WIDTH)
            grid_width = BOARD_WIDTH * cell_size
            grid_height = BOARD_HEIGHT * cell_size
            grid_x0 = (w - grid_width) // 2
            grid_y0 = (h - grid_height) // 2

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    # Safe exit
                    self.quit = True
                    break
                elif event.type == pg.VIDEORESIZE:
                    screen = pg.display.set_mode((event.w, event.h), pg.RESIZABLE)
                elif event.type == pg.MOUSEBUTTONDOWN and self.minesweeper: # Click
                    hit = self.mouse_to_grid(*event.pos, grid_x0, grid_y0, cell_size, BOARD_WIDTH, BOARD_HEIGHT)
                    if hit is None:
                        continue  # Clicked margin or outside grid
                    grid_x, grid_y = hit
                    if event.button == 1: # Left click reveal
                        self.minesweeper.reveal_square(grid_x, grid_y)
                    elif event.button == 3: # Right click flag
                        self.minesweeper.toggle_flag(grid_x, grid_y)

            # Draw the grid
            screen.fill(BACKGROUND)
            board = self.minesweeper.get_display_board()
            for y in range(self.minesweeper.height):
                for x in range(self.minesweeper.width):
                    value = board[y][x]
                    if self.minesweeper.revealed[y][x]:
                        if value == -1:
                            color = MINE_RED
                        elif value == 0:
                            color = REVEALED_EMPTY
                        else:
                            color = REVEALED_NUMBER
                    else:
                        color = HIDDEN

                    cell_rect = pg.Rect(grid_x0 + x * cell_size, grid_y0 + y * cell_size, cell_size, cell_size)
                    pg.draw.rect(screen, color, cell_rect)
                    pg.draw.rect(screen, GRID_LINE, cell_rect, 1)  # grid line

                    # draw text centered in the cell
                    if self.minesweeper.revealed[y][x]: # Draw number if revealed
                        txt = font.render(str(value if value >= 0 else 'X'), True, WHITE)
                        screen.blit(txt, txt.get_rect(center=cell_rect.center))
                    elif self.minesweeper.flags[y][x]: # Draw flag if flagged
                        txt = font.render("F", True, BACKGROUND)
                        screen.blit(txt, txt.get_rect(center=cell_rect.center))

            # Column labels A–J (top)
            for col_index, letter in enumerate("ABCDEFGHIJ"):
                text_surface = font.render(letter, True, GENERAL_TEXT)
                text_rect = text_surface.get_rect(center=(
                    grid_x0 + col_index * cell_size + cell_size // 2,
                    grid_y0 // 2
                ))
                screen.blit(text_surface, text_rect)

            # Row labels 1–10 (left)
            for row_index in range(BOARD_HEIGHT):
                text_surface = font.render(str(row_index + 1), True, GENERAL_TEXT)
                text_rect = text_surface.get_rect(center=(
                    grid_x0 // 2,
                    grid_y0 + row_index * cell_size + cell_size // 2
                ))
                screen.blit(text_surface, text_rect)

            # Flag Count
            flag_rect = pg.Rect(w/2, h*12/13, 10, 10)
            pg.draw.rect(screen, BACKGROUND, flag_rect)
            flags = font.render(f'Flags Remaining: {str(self.minesweeper.flags_remaining)}', True, WHITE)
            screen.blit(flags, flags.get_rect(center=flag_rect.center))
                
            # Game end
            if self.minesweeper.is_game_over(): # Loss
                win_width, win_height = screen.get_size()
                overlay = pg.Surface((win_width, win_height), pg.SRCALPHA) # Create an overlay surface that allows for transparency
                overlay.fill(TRANSPARENT_RED, (0, win_height // 2 - 30, win_width, 60)) 
                screen.blit(overlay, (0, 0))
                text = font.render("Game Over", True, BLACK)
                screen.blit(text, (win_width // 2 - text.get_width() // 2, win_height // 2 - text.get_height() // 2))
                pg.display.flip()
            elif self.minesweeper.is_game_won(): # Win
                win_width, win_height = screen.get_size()
                overlay = pg.Surface((win_width, win_height), pg.SRCALPHA) # Create an overlay surface that allows for transparency
                overlay.fill(TRANSPARENT_GREEN, (0, win_height // 2 - 30, win_width, 60)) 
                screen.blit(overlay, (0, 0))
                text = font.render("You Win!", True, BLACK)
                screen.blit(text, (win_width // 2 - text.get_width() // 2, win_height // 2 - text.get_height() // 2))
                pg.display.flip()

            pg.display.flip()
            clock.tick(60)
        self.exit_game()

Game.play_minesweeper()