turtlestats
============

*Easily track stats in games made with Turtle*

Add link to ReadTheDocs site


Features
----------

* Create a game with [turtle](https://docs.python.org/3/library/turtle.html).
* Decide what stats you want to track (final level, distance traveled, etc.)
* turtlestats tracks historical stats for you!
* You can use [turtlestats.display](#command-line-usage) to show plots of stats.
* Want to see all past stats? Look in the `.turtlestats/stats.sqlite` database in your code's home directory. You can use a tool like [SQLite browser](https://sqlitebrowser.org/) to view the database.

How to use
------------

0. Import `display_stats_in_game` from turtlestats. This will take care of all of your stats displaying needs.
1. To display your top scores, your game must have a `scoreboard` class that is a subclass of [turtle.Turtle](https://docs.python.org/3/library/turtle.html#methods-of-rawturtle-turtle-and-corresponding-functions) and tracks some in-game stats. The class doesn't need to have a particular name.
2. In your gameplay file, define an instance of the `scoreboard` object in the global environment.
3. Create a gameplay function that tracks all game actions.
    - Decorate this gameplay function as follows:
```py
# store score and level in the database (that's the second argument)
# alert the user at the end of each game if they got a high score (third arg)
@display_stats_in_game(scoreboard, {"score": float, "level": int}, "score")
def main():
    # gameplay logic
```
4. The `main` function shown above will now be augmented so that everytime you play the game, the `score` and `level` stats are logged in a database, and if you got the highest score, a little message will pop up congratulating the user.
5. The `scoreboard` class will also be augmented with `best_score` and `best_score_username` attributes, which you can use inside your code if you want to display those attributes in-game (e.g., by showing them while the user is playing)

How to integrate into existing code
------------

### Old code
```py
distance_traveled = 0
score = 0

while True:
    distance_traveled += 0.5
    if user_did_good_thing:
        score += 1
    if user_did_bad_thing:
        break
```

### New code
```py
from turtlestats import display_stats_in_game

class Scoreboard(Turtle):
    def __init__(self):
        super().__init__()
        self.distance_traveled = 0
        self.score = 0

scoreboard = Scoreboard()

@display_stats_in_game(scoreboard, {"distance_traveled": float, "score": int}, "score")
def main():
    while True:
        scoreboard.distance_traveled += 0.5
        if user_did_good_thing:
            scoreboard.score += 1
        if user_did_bad_thing:
            break

if __name__ == '__main__':
    main()
```

Command line usage
------------

- To make plots of stored stats, use `turtlestats.display` from the command line.
- You can use `python -m turtlestats.display` with no additional command line arguments to create a turtle GUI.

![Turtle GUI for turtlestats.display](/turtlestats%20plotting%20form.PNG)

- If you need help, `python -m turtlestats.display -h` will help.
- For example, `python -m turtlestats.display trend level --first_day 2022-09-10 --dirname "filepath\turtle_crossing" --img "filepath\turtle_crossing score trend.png"` will make an image file at `filepath\turtle_crossing score trend.png` based on the scores in the directory `filepath\turtle_crossing\.turtlestats` based on the highest level achieved for each day on the game [turtle-crossing](https://github.com/mcfarley1/turtle-crossing), and that image might look like this:

![Score trend for turtle crossing](/turtle_crossing%20score%20trend.png)

- Alternatively, you don't need to specify the dirname for turtlestats if you're already in the code directory of the game. For example, if you're already in the code directory of [Snake](https://github.com/mcfarley1/snake), then you can use turtlestats.display like so: `python -m turtlestats.display top_users score --num_top_users 4 --img "filepath\turtlestats\snake top 4 users.png"`, which gives the four highest-scoring users of all time for snake.

![Top 4 all-time users for Snake](/snake%20top%204%20users.png)

Dependencies
------------

- No dependencies outside the standard library for basic use.
- To use the `turtlestats.display` module to make plots of scores, you need [pandas](https://pypi.org/project/pandas/) and [matplotlib](https://pypi.org/project/matplotlib/).

Other stuff
------------

TODO: add code coverage link (the below link is broken)
(https://codecov.io/github/URL-OF-PROJECT?branch=master)](https://codecov.io/OTHER-URL-OF-PROJECT)