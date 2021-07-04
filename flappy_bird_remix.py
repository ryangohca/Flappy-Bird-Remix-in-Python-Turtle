"""A remake of the Flappy Bird Game.
Note that flappy.gif, green_flappy.gif, apple.gif, enchanted_golden_apple.gif
must be in the same directory as the file for this project to run.
flappy.gif and green_flappy.gif must be at about 60 * 50 pixels, and
apple.gif and enchanted_golden_apple.gif must be about 60 * 80
for the program to run correctly.
"""
from collections import deque
import random
import turtle
import logging
logging.basicConfig(level=logging.DEBUG)
logging.info("Logging started.")

# The screen
screen = turtle.Screen()
screen.setup(800, 600)
screen.bgcolor("lightblue")
screen.tracer(0)

# Bird image
player_image = "flappy.gif"
screen.addshape(player_image)

player_green_image = "green_flappy.gif"
screen.addshape(player_green_image)

# Apple images
apple_image = "apple.gif"
screen.addshape(apple_image)

golden_apple_image = "enchanted_golden_apple.gif"
screen.addshape(golden_apple_image)

# Listen for keypress, screen.
screen.listen()

# The player (as bird)
shape_size = (62, 47)
player = turtle.Turtle()
player.hideturtle()
player.shape(player_image)
player.penup()
player.speed(0)
player.pass_through_walls = False

# The turtle for writing start and game over messages
write_turtle = turtle.Turtle()
write_turtle.hideturtle()
write_turtle.speed(0)

# The turtle for writing score messages
score_turtle = turtle.Turtle()
score_turtle.hideturtle()
score_turtle.speed(0)

# The turtle for writing boost time messages
boost_turtle = turtle.Turtle()
boost_turtle.hideturtle()
boost_turtle.speed(0)

# Constants
move_speed = 40

# Gravity - the bird accelerates while falling too.
gravity_speed = 6

# Score of player
score = 0

# Check whether the game is running.
is_game_over = False

# Walls in game
wallsTop = deque()
wallsBottom = deque()

class Wall:
    wallid = 0
    def __init__(self, top_leftx, top_lefty, height, wall_colour):
        thickness = 30
        self.top_leftx = top_leftx
        self.top_lefty = top_lefty
        # Wall shape
        self.height = height
        self.length = thickness
        self.halfHeight = self.height / 2
        self.halfLen = self.length / 2
        wall_shape = turtle.Shape("compound")
        wall_points = ((-self.halfHeight, -self.halfLen),
                       (-self.halfHeight, self.halfLen),
                       (self.halfHeight, self.halfLen),
                       (self.halfHeight, -self.halfLen))
        wall_shape.addcomponent(wall_points, wall_colour)
        self.shapeName = "wall%d" % Wall.wallid # A unique name for this shape.
        screen.register_shape(self.shapeName, wall_shape)
        # Create wall
        self.wall = turtle.Turtle()
        self.wall.hideturtle()
        self.wall.speed(0)
        self.wall.shape(self.shapeName)
        self.wall.penup()
        self.wall.goto(top_leftx + self.halfLen, top_lefty - self.halfHeight)
        self.wall.stamp()
        Wall.wallid += 1

    def move_left(self, dist):
        self.wall.clear()
        self.wall.goto(self.wall.xcor() - 10, self.wall.ycor())
        self.wall.stamp()

    def remove_wall(self):
        self.wall.clear()
        self.wall.hideturtle()

    def out_of_bounds(self):
        return self.wall.xcor() < -screen.window_width() / 2

    def collide_with_player(self):
        x_dist = abs(self.wall.xcor() - player.xcor())
        y_dist = abs(self.wall.ycor() - player.ycor())
        overlap_horizontally = shape_size[0] / 2 + self.halfLen >= x_dist
        overlap_vertically = shape_size[1] / 2 + self.halfHeight >= y_dist
        return overlap_horizontally and overlap_vertically

# Apples in game
apples = deque()
apples_size = (59, 77)
class Apple:
    def __init__(self, x, y, image=apple_image):
        self.apple = turtle.Turtle()
        self.apple.shape(image)
        self.apple.penup()
        self.apple.hideturtle()
        self.x = x
        self.y = y
        self.apple.goto(x, y)
        self.apple.speed(0)
        self.apple.stamp()
        self.is_removed = False

    def move_left(self, dist):
        if self.is_removed:
            return # Removed apple should not move.
        self.apple.clear()
        self.apple.goto(self.apple.xcor() - 10, self.apple.ycor())
        self.apple.stamp()

    def remove_apple(self):
        self.apple.clear()
        self.apple.hideturtle()
        self.is_removed = True

    def out_of_bounds(self):
        return self.apple.xcor() < -screen.window_width() / 2
    
    def collide_with_player(self):
        x_dist = abs(self.apple.xcor() - player.xcor())
        y_dist = abs(self.apple.ycor() - player.ycor())
        overlap_horizontally = shape_size[0] / 2 + apples_size[0] / 2 >= x_dist
        overlap_vertically = shape_size[1] / 2 + apples_size[1] / 2 >= y_dist
        return overlap_horizontally and overlap_vertically

    def give_reward(self):
        global score
        logging.info("Player had eaten a regular apple and earned 3 points.")
        score += 3

numGoldenApplesEatenDuringBoost = 0        
boostTimeLeft = 0
class GoldenApple(Apple):
     # Every thing is the same as Apple, except for the rewards
     def __init__(self, x, y):
         super().__init__(x, y, image=golden_apple_image)
         
     def give_reward(self):
         global numGoldenApplesEatenDuringBoost, boostTimeLeft 
         player.pass_through_walls = True
         player.shape(player_green_image)
         numGoldenApplesEatenDuringBoost += 1
         logging.info("Player had eaten an enchanted golden apple. His effect of passing through walls will be refilled to 10s.")
         boostTimeLeft = 10
         screen.ontimer(self.remove_reward, 10000)

     def remove_reward(self):
         global numGoldenApplesEatenDuringBoost
         if numGoldenApplesEatenDuringBoost == 0:
             return # No golden apples eaten, no boost to cancel.
         numGoldenApplesEatenDuringBoost -= 1
         # Only the apple eaten last can cancel boost
         if numGoldenApplesEatenDuringBoost == 0:
             logging.info("Player's effect expired. He qould not be able to pass through walls.")
             player.pass_through_walls = False
             player.shape(player_image)
         
def penup_goto(t, x, y):
    t.penup()
    t.goto(x, y)

def reset():
    """Resets level."""
    # Prepare the global game state variables
    global is_game_over, gravity_speed, score, numGoldenApplesEatenDuringBoost, boostTimeLeft
    # Prevent the player from launching the game twice.
    # Due to concurrency, this may still happen if the player
    # spammed the Return key.
    screen.onkey(None, 'Return')
    # Player state global variables.
    player.shape(player_image)
    gravity_speed = 6
    is_game_over = False
    player.pass_through_walls = False
    numGoldenApplesEatenDuringBoost = 0
    boostTimeLeft = 0
    score = 0
    # Reset positons of turtles
    penup_goto(player, -300, 0)
    penup_goto(write_turtle, 0, 0)
    # Reset any writings
    write_turtle.clear()
    score_turtle.clear()
    # Delete all the walls
    for wall in wallsTop:
        wall.remove_wall()
    for wall in wallsBottom:
        wall.remove_wall()
    for apple in apples:
        apple.remove_apple()
    wallsTop.clear()
    wallsBottom.clear()
    apples.clear()
    # Start the game by adding the first obstacle
    add_new_wall()
    # Enable movement of bird after all setup is done.
    screen.onkey(up, "space")

def start_game():
    logging.info("Player started the game.")
    reset()
    mainloop()
    
def game_over():
    """Signal to the player that the game stops."""
    global is_game_over
    is_game_over = True
    screen.onkey(None, 'space') # Disable space.
    penup_goto(write_turtle, 0, 0)
    write_turtle.write("Game Over! You scored %d." % score, align="center", font=("Arial", 30, 'normal'))
    penup_goto(write_turtle, 0, -30)
    write_turtle.write("Press Enter/Return to play again.", align="center", font=("Arial", 15, 'normal'))
    screen.onkey(start_game, 'Return')
       
def up():
    """Move player up."""
    global gravity_speed
    gravity_speed = 6
    # If player would not exit the screen, move the player up.
    if player.ycor() + shape_size[1] / 2 + move_speed < screen.window_height() / 2:
        player.clear()
        player.goto(player.xcor(), player.ycor() + move_speed)
        player.stamp()

def force_move_player():
    """Move player down due to gravity."""
    global gravity_speed
    # Check whether the player touched the ground.
    if player.ycor() - shape_size[1] / 2 - gravity_speed <= -screen.window_height() / 2:
        logging.info("Player falled to death.")
        game_over()
        return
    player.clear()
    # Force the player to move down.
    player.goto(player.xcor(), player.ycor() - gravity_speed)
    player.stamp()
    gravity_speed *= 1.075 # Increase speed due to acceleration

def add_new_wall(t=4000):
    """Adds a new wall only when t >= 4000. Individual timer tracking needs to be done
       so that when the game stops, the timer to add an new wall stops."""
    if t >= 4000:
        wall_colour = random.choice(['green', 'red', 'yellow', 'blue'])
        logging.info("A %s wall had spawned." % wall_colour)
        # Amount of space height for the player to pass through
        space_height = random.randint(100, 250) # 100 - very difficult, 250 - easy
        # The top wall.
        top_height = random.randint(100, 450) # 450 - very difficult
        w = Wall(screen.window_width() / 2, screen.window_height() / 2, top_height, wall_colour)
        wallsTop.append(w)
        # The bottom wall
        bottom_height = screen.window_height() - space_height - top_height
        w = Wall(screen.window_width() / 2, -screen.window_height() / 2 + bottom_height, bottom_height, wall_colour)
        wallsBottom.append(w)
        # Set timer to a random number, to create another wall after a
        # random time between 2.5s - 4s.
        t = random.randint(0, 1500)
    if not is_game_over:
        # Run this function every 40ms, should be fast enough,
        # such that when the game abruptly ends, no extra walls
        # are made.
        screen.ontimer(lambda t=t+40: add_new_wall(t+40), 40)
    
def move_walls():
    if is_game_over:
        return
    global score
    # Move the wall
    for wall in wallsTop:
        wall.move_left(10)
    for wall in wallsBottom:
        wall.move_left(10)

    # Check whether the first seen wall is out of reach, can safely remove to save space.
    if len(wallsTop) != 0 and wallsTop[0].out_of_bounds():
        wallsTop[0].remove_wall()
        wallsTop.popleft()
        wallsBottom[0].remove_wall()
        wallsBottom.popleft()
        logging.info("Player successfully dodged a wall and earned 1 point.")
        score += 1

def check_for_wall_collisions():
    for wall in wallsTop:
        if wall.collide_with_player():
            if player.pass_through_walls:
                continue
            logging.info("Player died by hitting a wall.")
            game_over()
            return # no need to check anymore, player had hit a wall.
    for wall in wallsBottom:
        if wall.collide_with_player():
            if player.pass_through_walls:
                continue
            logging.info("Player died by hitting a wall.")
            game_over()
            return # no need to check anymore, player had hit a wall.
    
def check_for_apple_collisions():
    for apple in apples:
        # The method remove_apple does not actually remove the apple,
        # it only askes the apple to act like it is gone.
        # Actual removal only happens when the apple moves out of scope.
        # Therefore, it is important that we check whether the apple is disabled
        # and hidden from the player's view first before checking for collisions.
        if not apple.is_removed and apple.collide_with_player():
            apple.give_reward()
            apple.remove_apple()
    
def update_score():
    # The 50 pixels sentinal is to ensure that the text fully appears on screen.
    penup_goto(score_turtle, screen.window_width() / 2 - 50, screen.window_height() / 2 - 50)
    score_turtle.clear()
    score_turtle.write("Score: %d" % score, align='right', font=("Arial", 18, 'normal'))

def update_boost_time():
    # The 50 pixels sentinal is to ensure that the text fully appears on screen.
    penup_goto(boost_turtle, -screen.window_width() / 2 + 50, screen.window_height() / 2 - 50)
    boost_turtle.clear()
    boost_turtle.write("Effect Remaining Time: %ds" % boostTimeLeft, font=("Arial", 18, 'normal'))

def decreaseTimeLeft():
    global boostTimeLeft
    screen.ontimer(decreaseTimeLeft, 1000)
    if boostTimeLeft == 0:
        return # No time to subtract.
    boostTimeLeft -= 1
             
def move_apples():
    if is_game_over:
        return
    for apple in apples:
        apple.move_left(10)

    # Check whether any apple moves out of the screen.
    if len(apples) != 0 and apples[0].out_of_bounds():
        # If so, 'remove' it from player by hiding it, ...
        apples[0].remove_apple()
        # then do the actual removal.
        apples.popleft()

def add_apple(Apple):
    # The 50 pixel sentinal is to ensure that the apple appears fully on screen
    # for the player to collect.
    apple_starty = random.randint(-screen.window_height() / 2 + 50, screen.window_height() / 2 - 50)
    apples.append(Apple(screen.window_width() / 2, apple_starty))
    
def mainloop():
    if not is_game_over:
        force_move_player()
        move_walls()
        move_apples()
        # A golden apple is rarer than a normal one.
        if random.randint(1, 2000) > 1990:
            logging.info("A regular apple had spawned.")
            add_apple(Apple)
        if random.randint(1, 5000) > 4995:
            logging.info("An enchanted golden apple had spawned.")
            add_apple(GoldenApple)
        check_for_wall_collisions()
        check_for_apple_collisions()
        update_score()
        update_boost_time()
        screen.update()
        screen.ontimer(mainloop, 30)

def introduce_and_start_game():
    penup_goto(write_turtle, 0, 0)
    write_turtle.write(
    """Welcome to Flappy Bird!
This game is very simple: avoid the poles to earn points, 
and do not touch the ground too hard!
Press space to move the bird up, as gravity will pull it down.
Each time you pass through a wall, you score 1 point.
There are also apples in the game for you to eat.
If you ate a red apple, you score 3 bonus points.
If you ate a golden apple, you turn green, which means for 10s, you can
travel through walls! Any subsequent golden apple eaten when the effect is
active however, would only refill the timer back to 10s again.
If you are ready, press enter to enter the game.
Warning: Do not change the size of the screen!""",
    align='center', font=("Arial", 16, 'normal'))
    screen.onkey(start_game, 'Return')
    decreaseTimeLeft()

introduce_and_start_game()
