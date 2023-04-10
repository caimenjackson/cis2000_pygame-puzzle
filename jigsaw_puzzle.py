import pygame
import sys
import random
import pygame_gui
from pygame_gui.elements import UIButton, UIWindow, UILabel

pygame.init()

# Constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

RESIZED_WIDTH = int(SCREEN_WIDTH * 0.8)
RESIZED_HEIGHT = int(SCREEN_HEIGHT * 0.8) 

# Jigsaw puzzle configuration
num_rows = 2
num_columns = 2


# Colors
WHITE = (255, 255, 255)

# Initialize the screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jigsaw Puzzle")
clock = pygame.time.Clock()

def load_image_and_split():
    # Load the image and resize it
    image = pygame.image.load("image_two.png")
    image = pygame.transform.scale(image, (RESIZED_WIDTH, RESIZED_HEIGHT))

    # Calculate the size of each piece
    piece_width = image.get_width() // num_columns
    piece_height = image.get_height() // num_rows

    # Split the image into pieces
    pieces = []
    index = 0
    for row in range(num_rows):
        for col in range(num_columns):
            piece_rect = pygame.Rect(col * piece_width, row * piece_height, piece_width, piece_height)

            # Randomize the initial position
            random_x = random.randint(0, SCREEN_WIDTH - piece_width)
            random_y = random.randint(0, SCREEN_HEIGHT - piece_height)
            position_rect = pygame.Rect(random_x, random_y, piece_width, piece_height)

            pieces.append((image.subsurface(piece_rect), position_rect, index))
            index += 1

    return pieces

def is_puzzle_solved(pieces):
    position_tolerance = 5

    for i, (_, rect1, index1) in enumerate(pieces):
        for _, rect2, index2 in pieces[i+1:]:
            row1, col1 = divmod(index1, num_columns)
            row2, col2 = divmod(index2, num_columns)

            expected_x_diff = (col2 - col1) * rect1.width
            expected_y_diff = (row2 - row1) * rect1.height

            actual_x_diff = rect2.x - rect1.x
            actual_y_diff = rect2.y - rect1.y

            if abs(actual_x_diff - expected_x_diff) > position_tolerance or abs(actual_y_diff - expected_y_diff) > position_tolerance:
                return False

    return True




# Global variable to keep track of the selected piece
selected_piece = None

# Function to check if a point is inside a rectangle
def is_point_inside_rect(point, rect):
    x, y = point
    return rect.left <= x <= rect.right and rect.top <= y <= rect.bottom

# Constants for snapping
SNAP_DISTANCE = 100

def are_neighbors(pieces, piece1_idx, piece2_idx):
    row1, col1 = divmod(pieces[piece1_idx][2], num_columns)
    row2, col2 = divmod(pieces[piece2_idx][2], num_columns)

    return abs(row1 - row2) + abs(col1 - col2) == 1

def snap_pieces(pieces, selected_piece):
    _, selected_rect, selected_idx = pieces[selected_piece]

    for i, (_, rect, idx) in enumerate(pieces):
        if i == selected_piece:
            continue

        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:  # Check the four neighboring positions
            x_diff = abs(selected_rect.x - rect.x - dx * rect.width)
            y_diff = abs(selected_rect.y - rect.y - dy * rect.height)

            if (x_diff <= SNAP_DISTANCE and y_diff == 0 or x_diff == 0 and y_diff <= SNAP_DISTANCE) and are_neighbors(pieces, selected_idx, idx):
                selected_rect.x = rect.x + dx * rect.width
                selected_rect.y = rect.y + dy * rect.height
                return

def game_loop():
    global selected_piece

    pieces = load_image_and_split()

    ui_manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))


    exit_button = UIButton(relative_rect=pygame.Rect(0, 0, 80, 40), text="Exit", manager=ui_manager)
    learn_more_button = UIButton(relative_rect=pygame.Rect(80, 0, 120, 40), text="Learn more", manager=ui_manager)


    while True:
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == exit_button:
                        pygame.quit()
                        sys.exit()
                    elif event.ui_element == learn_more_button:
                        print("Learn more clicked!")

            


            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, (piece, rect, _) in enumerate(pieces):
                    if is_point_inside_rect(event.pos, rect):
                        selected_piece = i
                        break

            elif event.type == pygame.MOUSEMOTION:
                if selected_piece is not None:
                    piece, rect, _ = pieces[selected_piece]
                    rect.x, rect.y = event.pos

            elif event.type == pygame.MOUSEBUTTONUP:
                if selected_piece is not None:
                    # Check if the piece is close to any correct neighboring piece
                    snap_pieces(pieces, selected_piece)

                    # Check if the puzzle is solved
                    if is_puzzle_solved(pieces):
                        print("Puzzle solved!")
                    
                    selected_piece = None

            # Pass the events to the UIManager
            ui_manager.process_events(event)

        screen.fill(WHITE)

        # Draw the puzzle pieces
        for piece, rect, _ in pieces:
            screen.blit(piece, rect)

        time_delta = clock.tick(FPS) / 1000.0

        ui_manager.update(time_delta)
        ui_manager.draw_ui(screen)


        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    game_loop()
