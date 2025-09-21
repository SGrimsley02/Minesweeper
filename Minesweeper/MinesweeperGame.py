"""
Module: MinesweeperGame
Class: Game
Description: Organizes and runs the Minesweeper game using Pygame.
            Title screen, gameplay loop, rendering, and input handling.
Inputs: User interaction via GUI.
Outputs: Game window with interactive Minesweeper board.
External Sources: None
Authors: Kiara [Sam] Grimsley, Reeny Huang, Lauren D'Souza, Audrey Pan, Ella Nguyen, Hart Nurnberg
Created: September 19, 2025 (original prototype August 25, 2025)
Last Modified: September 19, 2025
"""

import os
import pygame as pg
import pygame_textinput as textinput
from MinesweeperBoard import Minesweeper

# Board layout (fixed 10x10)
BOARD_WIDTH = 10
BOARD_HEIGHT = 10

# Window size limit
MIN_WINDOW = (550, 550)

# Paths for assets
BASE_DIR = os.path.dirname(__file__)
FLAG_PATH = os.path.join(BASE_DIR, "Assets", "flag.png")
MINE_PATH = os.path.join(BASE_DIR, "Assets", "skull.png")
CURSOR_PATH = os.path.join(BASE_DIR, "Assets", "cursor.png")
FONT_PATH = os.path.join(BASE_DIR, "Assets", "pixelfont.ttf")

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRID_LINE = (255, 255, 255)
HIDDEN = (247, 225, 215)
REVEALED_EMPTY = (222, 219, 210)
REVEALED_NUMBER = (176, 196, 177)
MINE_RED = (219, 110, 110)
BACKGROUND = (74, 87, 89)
TITLE_TEXT = (240, 228, 220)
GENERAL_TEXT = (176, 196, 177)
TRANSPARENT_RED = (255, 155, 155, 180)
TRANSPARENT_GREEN = (155, 255, 155, 200)

class Game:
    def __init__(self):
        """Initialize the game."""
        self.minesweeper = None
        self.quit = False
        self.start_ticks = None  # Set when the game actually starts
        self.end_time = None     # Frozen final time
        pg.init()

    def start_game(self, width: int, height: int, num_mines: int):
        """Start a new minesweeper board with given width, height, and num_mines."""
        self.minesweeper = Minesweeper(width, height, num_mines)
        self.start_ticks = pg.time.get_ticks()  # milliseconds since pg.init()
        self.end_time = None

    def exit_game(self):
        """Perform any game cleanup here (if needed), then quit()."""
        pg.mouse.set_visible(True)
        pg.quit()

    def play_minesweeper():
        """Static method to play Minesweeper."""
        game = Game()
        game.run()

    def mouse_to_grid(self, mx: int, my: int, grid_x0, grid_y0, cell_size, grid_width, grid_height):
        """Convert mouse pixel coordinates (mx, my) to grid coordinates (gx, gy), or None if click outside of board"""
        if not (grid_x0 <= mx < grid_x0 + cell_size * grid_width # within grid x
                and grid_y0 <= my < grid_y0 + cell_size * grid_height): # within grid y
            return None # Clicked outside grid area
        gx = (mx - grid_x0) // cell_size
        gy = (my - grid_y0) // cell_size
        return int(gx), int(gy)

    def _clamp_size(self, w, h):
        """Clamp window size to minimum dimensions."""
        min_w, min_h = MIN_WINDOW
        w = max(min_w, w)
        h = max(min_h, h)
        return w, h


    def run(self):
        """Main game loop. Title screen followed by game."""
        screen = pg.display.set_mode((600, 600), pg.RESIZABLE)
        clock = pg.time.Clock()

        # Load assets, with defaults if loading fails
        try:
            font = pg.font.Font(FONT_PATH, 24)
            title_font = pg.font.Font(FONT_PATH, 30)
        except Exception as e:
            print("Custom font failed to load:", e)
            font = pg.font.SysFont(None, 24)
            title_font = pg.font.SysFont(None, 30)
        try:
            self.cursor_img = pg.image.load(CURSOR_PATH).convert_alpha()
            pg.mouse.set_visible(False) # Hide system cursor, use custom
        except Exception as e:
            print("Cursor image failed to load:", e)
            self.cursor_img = None
            pg.mouse.set_visible(True) # Show system cursor if custom fails
        try:
            self.flag_img = pg.image.load(FLAG_PATH).convert_alpha()
        except Exception as e:
            print("Flag image failed to load:", e)
            self.flag_img = None
        try:
            self.mine_img = pg.image.load(MINE_PATH).convert_alpha()
        except Exception as e:
            print("Mine image failed to load:", e)
            self.mine_img = None


        # Cap mines at 20 as per requirements. Validator restricts input to 2 digits, 0-20
        mines_input = textinput.TextInputVisualizer(manager=textinput.TextInputManager(validator=lambda x: (x.isdigit() and int(x) <= 20 and len(x) < 3) or x == ''),
                                                    font_object=font,
                                                    font_color=WHITE,
                                                    cursor_color=WHITE
                                                    )

        # Title screen loop
        while not self.minesweeper and not self.quit:
            screen.fill(BACKGROUND)
            pg.display.set_caption("Minesweeper -- Title Screen")

            # Responsive layout variables
            w, h = screen.get_size()
            x_center = w // 2
            title_margin = h * 0.3
            mine_text_margin = title_margin + h*0.1
            text_input_margin = mine_text_margin + h*0.1
            hint_margin = text_input_margin + h*0.1

            # Render title text centered at top
            title_text = title_font.render("Welcome to Minesweeper", True, TITLE_TEXT)
            title_text_rect = title_text.get_rect(center=(x_center, title_margin))
            screen.blit(title_text, title_text_rect)

            # Render text centered below title
            mines_text = font.render("Enter Mine Count (10-20): ", True, GENERAL_TEXT)
            mines_text_rect = mines_text.get_rect(center=(x_center, mine_text_margin))
            screen.blit(mines_text, mines_text_rect)

            # Updates mine and render mine-count input field
            events = pg.event.get()
            mines_input.update(events)
            mines_input_rect = mines_input.surface.get_rect(center=(x_center, text_input_margin))
            screen.blit(mines_input.surface, mines_input_rect)

            # Render hint text
            hint_text = font.render("Press Enter to Start", True, (GENERAL_TEXT))
            hint_text_rect = hint_text.get_rect(center=(x_center, hint_margin))
            screen.blit(hint_text, hint_text_rect)

            # Handle key presses and screen resize
            for event in events:
                if event.type == pg.QUIT:
                    # Safe exit
                    self.quit = True
                    break
                elif event.type == pg.VIDEORESIZE: # Resize window
                    new_w, new_h = self._clamp_size(event.w, event.h)
                    cur_w, cur_h = screen.get_size()
                    if (new_w, new_h) != (cur_w, cur_h):
                        screen = pg.display.set_mode((new_w, new_h), pg.RESIZABLE)
                elif event.type == pg.KEYDOWN and event.key == pg.K_RETURN: # Return/enter key
                    # Start game if mine count provided and within 10-20 range
                    if (mines_input.value and 10 <= int(mines_input.value) <= 20):
                        num_mines = int(mines_input.value)
                        self.start_game(BOARD_WIDTH, BOARD_HEIGHT, num_mines)

            # Custom cursor
            if self.cursor_img is not None:
                mx, my = pg.mouse.get_pos()
                screen.blit(self.cursor_img, (mx, my))

            pg.display.update()
            clock.tick(60)

        # Gameplay loop
        while not self.quit:
            if not self.minesweeper.is_game_over() and not self.minesweeper.is_game_won():
                pg.display.set_caption("Minesweeper -- Playing")
            w, h = screen.get_size()
            grid_size = min(w, h) * 0.8
            cell_size = int(grid_size // BOARD_WIDTH)
            grid_width = BOARD_WIDTH * cell_size
            grid_height = BOARD_HEIGHT * cell_size
            grid_x0 = (w - grid_width) // 2
            grid_y0 = (h - grid_height) // 2

            # Handle events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    # Safe exit
                    self.quit = True
                    break
                elif event.type == pg.VIDEORESIZE: # Resize window
                    new_w, new_h = self._clamp_size(event.w, event.h)
                    cur_w, cur_h = screen.get_size()
                    if (new_w, new_h) != (cur_w, cur_h):
                        screen = pg.display.set_mode((new_w, new_h), pg.RESIZABLE)
                elif event.type == pg.MOUSEBUTTONDOWN and self.minesweeper: # Click
                    hit = self.mouse_to_grid(*event.pos, grid_x0, grid_y0, cell_size, BOARD_WIDTH, BOARD_HEIGHT)
                    if hit is None:
                        continue  # Clicked margin or outside grid
                    grid_x, grid_y = hit
                    if event.button == 1: # Left click reveal
                        self.minesweeper.reveal_square(grid_x, grid_y)
                    elif event.button == 3: # Right click flag
                        self.minesweeper.toggle_flag(grid_x, grid_y)

            # Update timer
            if self.start_ticks is not None:
                if self.end_time is not None: # Game over, freeze timer
                    elapsed_seconds = self.end_time
                else:
                    elapsed_seconds = (pg.time.get_ticks() - self.start_ticks) // 1000
            else:
                elapsed_seconds = 0

            # Draw the grid
            screen.fill(BACKGROUND)
            board = self.minesweeper.get_display_board()
            for y in range(self.minesweeper.height):
                for x in range(self.minesweeper.width):
                    value = board[y][x]
                    # Determine color and icon of squares
                    icon = None
                    if value == -1:
                        color = MINE_RED
                        icon_size = int(cell_size * 0.5)
                        if self.mine_img is not None:
                            icon = pg.transform.smoothscale(self.mine_img, (icon_size, icon_size))
                        else: ## Default red if can't load mine image
                            icon = pg.Surface((icon_size, icon_size))
                            icon.fill(MINE_RED)
                    elif value == 0:
                        color = REVEALED_EMPTY
                        icon = font.render("0", True, WHITE)
                    elif value == "?":
                        color = HIDDEN
                        icon = None # No icon for hidden squares
                    elif value == "F":
                        color = HIDDEN
                        icon_size = int(cell_size * 0.5)
                        if self.flag_img is not None:
                            icon = pg.transform.smoothscale(self.flag_img, (icon_size, icon_size))
                        else:  # Default black if can't load flag image
                            icon = pg.Surface((icon_size, icon_size))
                            icon.fill(BLACK)
                    else:
                        color = REVEALED_NUMBER
                        icon = font.render(str(value), True, WHITE)

                    # Draw cell rectangle and icon if any
                    cell_rect = pg.Rect(grid_x0 + x * cell_size, grid_y0 + y * cell_size, cell_size, cell_size)
                    pg.draw.rect(screen, color, cell_rect)
                    pg.draw.rect(screen, GRID_LINE, cell_rect, 1)  # grid line
                    if icon is not None:
                        screen.blit(icon, icon.get_rect(center=cell_rect.center))

            # Draw labels and UI elements
            # Column labels A–J (top)
            for col_index, letter in enumerate("ABCDEFGHIJ"):
                text_surface = font.render(letter, True, GENERAL_TEXT)
                text_rect = text_surface.get_rect(center=(
                    grid_x0 + col_index * cell_size + cell_size // 2,
                    grid_y0 - 20
                ))
                screen.blit(text_surface, text_rect)

            # Row labels 1–10 (left)
            for row_index in range(BOARD_HEIGHT):
                text_surface = font.render(str(row_index + 1), True, GENERAL_TEXT)
                text_rect = text_surface.get_rect(center=(
                    grid_x0 - 20,
                    grid_y0 + row_index * cell_size + cell_size // 2
                ))
                screen.blit(text_surface, text_rect)

            # Timer display
            time_text = font.render(f"TIME: {elapsed_seconds}", True, GENERAL_TEXT)
            screen.blit(time_text, (
                w - time_text.get_width() - 10,
                h - time_text.get_height() - 10
            ))

            # Flag Count
            flag_rect = pg.Rect(w/2, h*12/13, 10, 10)
            pg.draw.rect(screen, BACKGROUND, flag_rect)
            flags = font.render(f'Flags Remaining: {str(self.minesweeper.flags_remaining)}', True, WHITE)
            screen.blit(flags, flags.get_rect(center=flag_rect.center))

            # Game end screen overlay
            if self.minesweeper.is_game_over(): # Loss
                pg.display.set_caption("Minesweeper -- You Lose")
                if self.end_time is None: # Freeze final time
                    self.end_time = (pg.time.get_ticks() - self.start_ticks) // 1000
                win_width, win_height = screen.get_size()
                overlay = pg.Surface((win_width, win_height), pg.SRCALPHA) # Create an overlay surface that allows for transparency
                overlay.fill(TRANSPARENT_RED, (0, win_height // 2 - 30, win_width, 60))
                screen.blit(overlay, (0, 0))
                text = font.render("Game Over", True, BLACK)
                screen.blit(text, (win_width // 2 - text.get_width() // 2, win_height // 2 - text.get_height() // 2))
            elif self.minesweeper.is_game_won(): # Win
                pg.display.set_caption("Minesweeper -- You Win!")
                if self.end_time is None: # Freeze final time
                    self.end_time = (pg.time.get_ticks() - self.start_ticks) // 1000
                win_width, win_height = screen.get_size()
                overlay = pg.Surface((win_width, win_height), pg.SRCALPHA) # Create an overlay surface that allows for transparency
                overlay.fill(TRANSPARENT_GREEN, (0, win_height // 2 - 30, win_width, 60))
                screen.blit(overlay, (0, 0))
                text = font.render("You Win!", True, BLACK)
                screen.blit(text, (win_width // 2 - text.get_width() // 2, win_height // 2 - text.get_height() // 2))

            # Custom cursor
            if self.cursor_img is not None:
                mx, my = pg.mouse.get_pos()
                screen.blit(self.cursor_img, (mx, my))

            pg.display.flip()
            clock.tick(60)
        self.exit_game()