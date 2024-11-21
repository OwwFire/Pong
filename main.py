import random
import threading
import time

from game_etup import *
from exceptions import *
from sys import stderr

game_running: bool = True
player_collision_flag: bool = False
bot_collision_flag: bool = False
goal_flag: bool = False
player_points: int = 0
bot_points: int = 0

# Speed variables
# Higher => slower , Lower => faster
player_rectangle_movement_divider: float = 3.0
bot_rectangle_movement_divider: float = 4.9
ball_movement_divider: float = 2.5
player_rectangle_movement_speed: float = (screen.get_width() / player_rectangle_movement_divider)
bot_rectangle_movement_speed: float = (screen.get_width() / bot_rectangle_movement_divider)
ball_top_movement_speed: float = 0
ball_left_movement_speed: float = 0

# Constants
MAX_POINTS: Final = 10
RECTANGLE_WIDTH: Final = 40
RECTANGLE_HEIGHT: Final = 80
BALL_RADIUS: Final = 15
BORDER_WIDTH: Final = 1
MIN_TOP_DISTANCE_FROM_EDGE: Final = 35
MIN_LEFT_DISTANCE_FROM_EDGE: Final = 20
MAX_TOP_DISTANCE_FROM_EDGE: Final = (screen.get_height() - MIN_LEFT_DISTANCE_FROM_EDGE)
MAX_LEFT_DISTANCE_FROM_EDGE: Final = (screen.get_width() - MIN_TOP_DISTANCE_FROM_EDGE)
PLAYER_RECTANGLE_COLOR: Final = "red"
BOT_RECTANGLE_COLOR: Final = "Blue"
BORDER_COLOR: Final = "black"
BALL_COLOR = "white"
BACKGROUND_COLOR: Final = "cyan"

# Objects positioning
player_left_position: float = MIN_TOP_DISTANCE_FROM_EDGE
player_top_position: float = (screen.get_height() / 2) - RECTANGLE_HEIGHT + MIN_TOP_DISTANCE_FROM_EDGE
bot_left_position: float = ((screen.get_width() - RECTANGLE_WIDTH) - MIN_TOP_DISTANCE_FROM_EDGE)
bot_top_position: float
ball_top_position: int = (screen.get_height() / 2)
ball_left_position: int = (screen.get_width() / 2)


class InitBallMovementThread(threading.Thread):
    def run(self):
        global ball_top_movement_speed, ball_left_movement_speed, player_top_position, bot_top_position
        ball_top_movement_speed = 0
        ball_left_movement_speed = 0
        bot_top_position = (screen.get_height() / 2) - RECTANGLE_HEIGHT + MIN_TOP_DISTANCE_FROM_EDGE

        time.sleep(1)

        movement_options = [-1, 1]
        random_movement_direction = random.choice(movement_options)
        ball_top_movement_speed = (screen.get_height() / ball_movement_divider) * random_movement_direction
        ball_left_movement_speed = (screen.get_width() / ball_movement_divider) * -1
        print(ball_top_movement_speed)
        print(ball_left_movement_speed)


def run_game_loop() -> None:
    """
    Maintains the execution of the game
    """
    global ball_top_position, ball_left_position, ball_top_movement_speed, ball_left_movement_speed
    delta_time: float = 1
    pygame.display.set_caption(f"PONG {player_points} - {bot_points}")
    ball_top_position = (screen.get_height() / 2)
    ball_left_position = (screen.get_width() / 2)
    InitBallMovementThread().start()
    while game_running:
        # Checking if the game was closed
        is_game_closed_by_player()
        # Clearing the screen
        screen.fill(BACKGROUND_COLOR)
        # Moving objects
        move_player_rectangle(pygame.key.get_pressed(), delta_time)
        move_bot_rectangle(delta_time)
        move_ball(delta_time)
        # Rendering objects
        render_objects()
        # Checking events
        check_player_collision()
        check_bot_collision()
        check_goal()
        # Updating the display
        pygame.display.update()
        # limits FPS to FRAME_RATE
        delta_time = clock.tick(FRAME_RATE) / 1000  # Converting clock time to seconds


def render_objects() -> None:
    """
    Renders all necessary objects
    """
    player_rectangle = pygame.Rect(player_left_position, player_top_position,
                                   RECTANGLE_WIDTH, RECTANGLE_HEIGHT)
    bot_rectangle = pygame.Rect(bot_left_position, bot_top_position,
                                RECTANGLE_WIDTH, RECTANGLE_HEIGHT)

    player_border = pygame.Rect(player_rectangle.left, player_rectangle.top,
                                player_rectangle.width + BORDER_WIDTH, player_rectangle.height + BORDER_WIDTH)
    bot_border = pygame.Rect(bot_rectangle.left, bot_rectangle.top,
                             bot_rectangle.width + BORDER_WIDTH, bot_rectangle.height + BORDER_WIDTH)
    # Drawing all objects
    pygame.draw.rect(screen, PLAYER_RECTANGLE_COLOR, player_rectangle)
    pygame.draw.rect(screen, BORDER_COLOR, player_border, width=BORDER_WIDTH)
    pygame.draw.rect(screen, BOT_RECTANGLE_COLOR, bot_rectangle)
    pygame.draw.rect(screen, BORDER_COLOR, bot_border, width=BORDER_WIDTH)
    pygame.draw.circle(screen, BALL_COLOR, (ball_left_position, ball_top_position), BALL_RADIUS)
    pygame.draw.circle(screen, BORDER_COLOR, (ball_left_position, ball_top_position), BALL_RADIUS + BORDER_WIDTH,
                       width=BORDER_WIDTH)


def move_player_rectangle(keys: list[str], delta_time: int) -> None:
    """
    Moves a player object accordingly to the key.\n
    :param keys: the key that was pressed
    :param delta_time: helps sync with the clock
    """
    global player_top_position
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        player_top_position -= player_rectangle_movement_speed * delta_time
        player_top_position = max(player_top_position, MIN_LEFT_DISTANCE_FROM_EDGE)
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        player_top_position += player_rectangle_movement_speed * delta_time
        player_top_position = min(player_top_position, screen.get_height() - RECTANGLE_HEIGHT
                                  - MIN_LEFT_DISTANCE_FROM_EDGE)


def move_bot_rectangle(delta_time: int) -> None:
    """
    Moves the bot object accordingly to the ball movement.\n
    :param delta_time: helps sync with the clock
    """
    global bot_top_position, ball_top_movement_speed

    # If the game is paused
    if ball_top_movement_speed == 0 or ball_left_movement_speed == 0:
        return

    if ball_top_movement_speed < 1:
        bot_top_position -= bot_rectangle_movement_speed * delta_time
        bot_top_position = max(bot_top_position, MIN_LEFT_DISTANCE_FROM_EDGE)
    else:
        bot_top_position += bot_rectangle_movement_speed * delta_time
        bot_top_position = min(bot_top_position, screen.get_height() - RECTANGLE_HEIGHT
                               - MIN_LEFT_DISTANCE_FROM_EDGE)


def move_ball(delta_time) -> None:
    """
    Moves the ball automatically
    :param delta_time: helps sync with the clock
    """
    global ball_top_position, ball_left_position, ball_left_movement_speed, ball_top_movement_speed
    global MAX_TOP_DISTANCE_FROM_EDGE

    ball_top_position += ball_top_movement_speed * delta_time
    ball_left_position += ball_left_movement_speed * delta_time

    if ball_top_position >= MAX_TOP_DISTANCE_FROM_EDGE:
        ball_top_movement_speed *= -1
    if ball_top_position <= MIN_TOP_DISTANCE_FROM_EDGE:
        ball_top_movement_speed *= -1
    if ball_left_position >= MAX_LEFT_DISTANCE_FROM_EDGE:
        ball_left_movement_speed *= -1
    if ball_left_position <= MIN_LEFT_DISTANCE_FROM_EDGE:
        ball_left_movement_speed *= -1


def check_player_collision() -> None:
    """
    Checks a collision of the ball with the player rectangle.\n
    If a collision occurred it will change the ball's direction accordingly.
    """
    global player_collision_flag
    player_collision_in_top = int(ball_top_position) in range(int(player_top_position),
                                                              int(player_top_position + RECTANGLE_HEIGHT))
    player_collision_in_left = int(ball_left_position) in range(int(player_left_position),
                                                                int(player_left_position +
                                                                    RECTANGLE_WIDTH + BALL_RADIUS))
    if not player_collision_flag and player_collision_in_top and player_collision_in_left:
        if (player_top_position + (int(player_top_position + RECTANGLE_HEIGHT))) // 2 < int(ball_top_position):
            change_ball_direction(top_flag=False)
        else:
            change_ball_direction()
        player_collision_flag = True
    if player_collision_flag and not player_collision_in_top and not player_collision_in_left:
        player_collision_flag = False


def check_bot_collision() -> None:
    """
    Checks a colnlision of the ball with the bot rectangle.\n
    If a collisio occurred it will change the ball's direction accordingly.
    """
    global bot_collision_flag, bot_top_position, bot_left_position
    bot_collision_in_top = int(ball_top_position) in range(int(bot_top_position),
                                                           int(bot_top_position + RECTANGLE_HEIGHT))
    bot_collision_in_left = int(ball_left_position) in range(int(bot_left_position),
                                                             int(bot_left_position +
                                                                 RECTANGLE_WIDTH + BALL_RADIUS))
    if not bot_collision_flag and bot_collision_in_top and bot_collision_in_left:
        if (bot_collision_in_top + (int(ball_top_position + RECTANGLE_HEIGHT))) // 2 < int(ball_top_position):
            change_ball_direction(top_flag=False)
        else:
            change_ball_direction()
        bot_collision_flag = True
    if bot_collision_flag and not bot_collision_in_top and not bot_collision_in_left:
        bot_collision_flag = False


def check_goal() -> None:
    """
    Checks if a goal was conceded, if so the round ends and a point is added accordingly.
    """
    global ball_left_position, bot_left_position, player_left_position
    global bot_collision_flag, player_collision_flag, goal_flag
    global player_points, bot_points
    if not goal_flag and ball_left_position < player_left_position and not player_collision_flag:
        bot_points += 1
        end_round()
        goal_flag = True
    if not goal_flag and ball_left_position > bot_left_position and not bot_collision_flag:
        player_points += 1
        end_round()
        goal_flag = True


def change_ball_direction(left_flag=True, top_flag=True) -> None:
    """
    Changes the direction of the moving ball
    :param left_flag: Do you want to change the left movement direction
    :param top_flag: Do you want to change the left movement direction
    """
    global ball_left_movement_speed, ball_top_movement_speed
    if top_flag:
        ball_top_movement_speed *= -1
    if left_flag:
        ball_left_movement_speed *= -1


def stop_game() -> None:
    """
    Stops a running game
    """
    raise PlayerExitedGameException


def end_round() -> None:
    """
    Ends a current round.
    """
    global game_running, ball_top_position, ball_left_position
    global ball_left_movement_speed, ball_top_movement_speed
    game_running = False
    ball_top_position = (screen.get_height() / 2)
    ball_left_position = (screen.get_width() / 2)


def is_game_closed_by_player() -> None:
    """
    Checks if a player exited the game.
    :return:
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # User clicked x on the window
            stop_game()


def close_game() -> None:
    """
    Closes the game
    """
    pygame.quit()


def main():
    global game_running, goal_flag
    # All functions required to run the game, closing the game regardless of run result
    try:
        while player_points < MAX_POINTS and bot_points < MAX_POINTS:
            game_running = True
            goal_flag = False
            run_game_loop()

    except Exception as error:
        print(error.with_traceback(), file=stderr)
    finally:
        close_game()


if __name__ == "__main__":
    main()
