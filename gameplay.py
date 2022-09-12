'''
integrates stats into gameplay
'''
import functools
import turtle
from turtle import Turtle
from turtlestats.stats import StatsHolder, function

def display_stats_in_game(scoreboard: Turtle,
                          stats: dict[str, type],
                          stat_of_interest: str = None) -> function:
    def wrapper(gameplay_function: function) -> None:
        @functools.wraps(gameplay_function)
        def outfunc(*args, **kwargs):
            screen = scoreboard.screen
            scoreboard.best_score = 0
            scoreboard.best_score_username = "???"
            hldr = StatsHolder(stats, scoreboard)
            if stat_of_interest:
                best_score_rows = hldr.top_by_stat(stat_of_interest, 1)
                if best_score_rows:
                    best_score_row = best_score_rows[0]
                    scoreboard.best_score_username = best_score_row['username']
                    scoreboard.best_score = best_score_row[stat_of_interest]
            username = ""
            while username == "":
                username = screen.textinput("User name", "Enter user name")
                screen.listen()
                if username is None:
                    username = "Anon"
            gameplay_function(*args, **kwargs)
            hldr.store(username)
            if stat_of_interest:
                score_of_interest = getattr(scoreboard, stat_of_interest)
                if score_of_interest > scoreboard.best_score:
                    screen.textinput("HIGH SCORE!!!", 
                        "Congratulations! You got the highest score ever!")
        return outfunc
    
    return wrapper