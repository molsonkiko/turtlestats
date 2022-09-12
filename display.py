'''make visualizations of stats
'''
# standard lib packages
import datetime
import os
import re
import sqlite3
import traceback
from turtle import Screen
# third-party packages
import pandas as pd
import matplotlib.pyplot as plt

FIRST_UNIX_DAY = str(datetime.date(1970, 1, 1))


def get_dbname(code_dir: str = None):
    if code_dir is None:
        code_dir = os.getcwd()
    dbname = os.path.join(code_dir, ".turtlestats", "stats.sqlite")
    if not os.path.exists(dbname):
        raise ValueError(f"No turtlestats database in {code_dir}")
    return dbname


def get_rows(code_dir, query = "SELECT * FROM stats", params=None):
    dbname = get_dbname(code_dir)
    with sqlite3.connect(dbname) as con:
        return pd.read_sql(query, con, params=params)


def best_score_bar(stat: str, 
                         first_day: datetime.date = None,
                         code_dir: str = None,
                         img_name: str = None):
    '''plot the trend of best scores by day'''
    if first_day is None:
        first_day = FIRST_UNIX_DAY
    df = get_rows(code_dir,
        f'''
SELECT date, mx FROM 
    (SELECT date, MAX({stat}) mx 
    FROM stats GROUP BY date)
WHERE date > ?
ORDER BY date''',
    (first_day,)
    )
    if not len(df):
        return
    fig, ax = plt.subplots()
    df.plot.bar(x='date', y='mx', ax=ax, legend=None)
    plt.xlabel("Date")
    plt.ylabel(stat)
    plt.title(f"Top {stat} by date")
    plt.tight_layout()
    if img_name:
        plt.savefig(img_name)
    plt.show()


def top_users_bar(stat: str, 
              num_top_users: int = 10, 
              code_dir: str = None,
              img_name: str = None):
    '''bar plot of top users by stat'''
    df = get_rows(code_dir, f'''
SELECT * FROM
    (SELECT username, MAX({stat}) mx 
    FROM stats GROUP BY username)
ORDER BY mx DESC
    '''
    )
    num_top_users = min(num_top_users, len(df))
    if num_top_users == 0:
        return
    fig, ax = plt.subplots()
    df.plot.bar(x='username', y='mx', ax=ax, legend=None)
    plt.xlabel("User name")
    plt.ylabel(stat)
    plt.title(f"Top {num_top_users} users by {stat}")
    plt.tight_layout()
    if img_name:
        plt.savefig(img_name)
    plt.show()


def turtle_plot_maker():
    '''use turtle and input boxes to choose what kind of
    plot to make'''
    screen = Screen()
    screen.title("turtlestats plotting form")
    plot_type = ''
    while True:
        plot_type = screen.textinput("Type of plot", "Enter a plot type (must be 'top_users' or 'trend')")
        screen.listen()
        if plot_type is None:
            return
        if plot_type != 'top_users' and plot_type != 'trend':
            print(f"'{plot_type}'' is not a valid plot type")
        else:
            break
    code_dir = ''
    while not os.path.isdir(code_dir):
        code_dir = screen.textinput("Path to directory containing the game", 
        "Enter the path to the code directory. '.' is the current directory.")
        screen.listen()
        if code_dir is None:
           return
        try:
            code_dir = os.path.abspath(code_dir)
            get_dbname(code_dir)
        except ValueError as ex:
            print(f"{code_dir} is not a directory containing a turtlestats database")
            code_dir = ''
    df = get_rows(code_dir)
    stats = list(df.columns[~df.columns.isin(['date', 'username'])])
    stat = ''
    while True:
        stat = screen.textinput("Statistic to plot", "Enter a stat name")
        screen.listen()
        if stat is None:
            return
        if stat in stats:
            break
        else:
            print(f'The stat must be one of {stats}')
    if plot_type == 'top_users':
        num_top_users = 10
        while True:
            num_top_users_str = screen.textinput("Number of top users", "Enter a number of top users (default 10)")
            screen.listen()
            if num_top_users_str is None:
                break
            try:
                num_top_users = int(num_top_users_str)
                break
            except:
                print('Must be a whole number')
        try:
            top_users_bar(stat, num_top_users, code_dir)
        except Exception as ex:
            want_see_err = screen.textinput("Error while trying to plot data", "Whoops, we couldn't plot your data! Want to see the error message?")
            if want_see_err is not None:
                traceback.print_exc(ex)
    elif plot_type == 'trend':
        first_day = FIRST_UNIX_DAY
        while True:
            first_day = screen.textinput("Earliest day to get data for", "Enter a date in YYYY-MM-DD format, or Cancel to get all dates")
            if first_day is None:
                break
            if re.fullmatch("\d{4}-\d{2}-\d{2}", first_day):
                break
        try:
            best_score_bar(stat, first_day, code_dir)
        except Exception as ex:
            want_see_err = screen.textinput("Error while trying to plot data", "Whoops, we couldn't plot your data! Want to see the error message?")
            if want_see_err is not None:
                traceback.print_exc(ex)
        

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("plot_type", 
        help="The type of plot to be created. Choices are 'trend' and 'top_users'",
        nargs='?',
        default = None)
    parser.add_argument('stat', 
        help='The stat of interest',
        nargs='?',
        default=None)
    parser.add_argument('--num_top_users', 
        type=int, 
        nargs='?', 
        help="If making a 'top_users' plot, the number of users to show (default 10)", 
        default=10,
        dest='num_top_users')
    parser.add_argument('--first_day', 
        nargs='?', 
        help="If making a 'trend' plot, the earliest day to consider scores for",
        default=FIRST_UNIX_DAY,
        dest = 'first_day')
    parser.add_argument('--dirname', 
        help="The name of the directory to read stats from (default current dir)", 
        nargs='?', 
        default=None, 
        dest='dirname')
    parser.add_argument('--img', 
        help='Name of the image file to write to (default none)', 
        nargs='?', 
        default=None,
        dest='img_name')
    args = parser.parse_args()
    if args.plot_type == None:
        turtle_plot_maker()
    if args.plot_type == 'trend':
        best_score_bar(args.stat, args.first_day, args.dirname, args.img_name)
    elif args.plot_type == 'top_users':
        top_users_bar(args.stat, args.num_top_users, args.dirname, args.img_name)