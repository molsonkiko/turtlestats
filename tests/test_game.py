'''
a simple game where you press some combination of the up and down keys
20 times.
Decorated with display_stats_in_game, and run using pyautogui 
in test.py.
'''
import turtle
from turtle import Turtle

from turtlestats.gameplay import display_stats_in_game

class Scoreboard(Turtle):
    def __init__(self, distance_per_up = 0.5):
        super().__init__()
        self.ups = 0
        self.downs = 0
        self.distance = 0.0
        self.distance_per_up = distance_per_up
        self.more_ups = False

    def up(self):
        self.ups += 1
        self.distance += self.distance_per_up
        if self.ups > self.downs:
            self.more_ups = True
        self.write_distance()

    def down(self):
        self.downs += 1
        self.distance -= self.distance_per_up
        if self.ups < self.downs:
            self.more_ups = False
        self.write_distance()

    def write_distance(self):
        self.clear()
        self.write(f"Distance traveled: {self.distance}", font=("Comic Sans", 20, "bold"))


sb = Scoreboard()
sb.screen.title('Turtlestats test game')


@display_stats_in_game(sb, {'more_ups': bool, 'ups': int, 'downs': int, 'distance': float}, 'distance')
def main():
    dist_per_up = sb.screen.numinput("Distance per up", "Enter the distance traveled per press of the up key, or Cancel to accept the default of 0.5")
    sb.screen.listen()
    if dist_per_up is None:
        dist_per_up = 0.5
    sb.distance_per_up = dist_per_up
    turtle.onkeypress(sb.up, 'Up')
    turtle.onkeypress(sb.down, 'Down')
    while sb.ups + sb.downs < 20:
        sb.screen.update()

if __name__ == '__main__':
    main()