'''
integrates stats into gameplay
'''
import datetime
import functools
from turtle import Turtle
from turtlestats.stats import StatsHolder, function

today = datetime.date.today

def display_stats_in_game(scoreboard: Turtle,
                          stats: dict[str, type],
                          stat_of_interest: str = None) -> function:
    '''scoreboard: a Turtle that holds stats of interest.
stats: a dict where the keys are names of stats (these must be names
    of attributes of the scoreboard) and each value is the type of a stat.
    So for a scoreboard that tracks `score` (a float) and `enemies_killed`
    (an int), stats might be {"score": float, "enemies_killed": int}
stat_of_interest: the name of the stat that you want to compare to past scores.
    If you don't want to do this, just leave it blank.
    If you do, the screen will show a message congratulating the user
    at the end of the game if they got a high score in that game
    (e.g., best score of all time, best score so far today)'''
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
            best_score_for_user_rows = hldr.top_by_stat_by_user(username, 
                stat_of_interest)
            best_score_today_rows = hldr.top_by_stat_on_date(today(), stat_of_interest)
            hldr.store(username)
            if stat_of_interest:
                score_of_interest = getattr(scoreboard, stat_of_interest)
                if score_of_interest > scoreboard.best_score:
                    screen.textinput("HIGH SCORE!!!", 
                        "Congratulations! You got the highest score ever!")
                    return
                best_score_for_user = float('inf')
                if best_score_for_user_rows:
                    best_score_for_user = best_score_for_user_rows[0][stat_of_interest]
                if score_of_interest > best_score_for_user:
                    screen.textinput("Personal high score",
                        "This is your best score yet!")
                    return
                best_score_today = float('inf')
                if best_score_today_rows:
                    best_score_today = best_score_today_rows[0][stat_of_interest]
                if score_of_interest > best_score_today:
                    screen.textinput("Best score of the day!",
                        "Congratulations! This is the top score so far today!")

        return outfunc
    
    return wrapper