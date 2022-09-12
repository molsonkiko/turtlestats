'''
Manages read/write of stats.
'''
import datetime
import functools
import inspect
import os
import sqlite3
from typing import Union
from turtle import Turtle

from turtlestats.utils import sqlite_typename

function = type(lambda x: x)

def setup_db_dir(scoreboard: Turtle) -> tuple[str, bool]:
    '''
    Creates a ".turtlestats" directory in the source
    directory of a scoreboard (turtle object)
    Returns the directory name, and bool(the directory already existed)
    '''

    src_fname = inspect.getabsfile(scoreboard.__class__)
    src_dir = os.path.dirname(src_fname)
    stats_dir = os.path.join(src_dir, ".turtlestats")
    if not os.path.exists(stats_dir):
        os.mkdir(stats_dir)
        return stats_dir, True
    return stats_dir, False

CREATE_TABLE_BASE = "CREATE TABLE stats (\n    username TEXT,\n    date TEXT,"

def make_stats_db(stats: dict[str, type], dbname: str) -> None:
    '''
stats: a dict mapping names of scoreboard stats (e.g., score, distance
    traveled to the type of that stat)

If the database dbname exists, do nothing.
If the database dbname doesn't exist, 
    execute a SQLite CREATE TABLE statement that makes a table with columns
    for the desired stats as well as the username and the date.
EXAMPLES
___________
make_stats_db({"winner": bool, "left_score": float, "right_score": float})
executes the query 'CREATE TABLE stats (\n    username TEXT,\n    date TEXT,\n    winner INT,\n    left_score REAL,\n    right_score REAL\n);'
    '''
    dbdef = CREATE_TABLE_BASE
    ii = 0
    for statname, typ in stats.items():
        ii += 1
        typename = sqlite_typename(typ)
        dbdef += f'\n    {statname} {typename}'
        if ii < len(stats):
            dbdef += ','
    dbdef += '\n);'
    # print(dbdef)
    if not os.path.exists(dbname):
        con = sqlite3.connect(dbname)
        try:
            con.executescript(dbdef)
        except Exception as ex:
            con.rollback()
            raise ex
        else:
            con.commit()
        finally:
            con.close()


def with_connection(meth):
    """Connect to the database at the file path of a StatsHolder's dbname,
    try to perform the method's function, commit if successful,
    clean up if there's an error, and finally close the database."""

    @functools.wraps(meth)
    def wrapper(*args, **kwargs):
        holder = args[0]
        holder.con = sqlite3.connect(holder.dbname)
        holder.con.row_factory = sqlite3.Row
        try:
            out = meth(*args, **kwargs)
        except Exception as ex:
            holder.con.rollback()
            raise ex
        else:
            # print(f'commited transaction from method {meth} with args {args} and kwargs {kwargs}')
            holder.con.commit()
            return out
        finally:
            holder.con.close()
            holder.con = None

    return wrapper


class StatsHolder:
    """A wrapper around a SQLite database containing usernames, dates,
    and various stats.

    Contains functions for getting rows that have top stats.
    """
    dbname: str
    insert_query: str
    con: sqlite3.Connection
    _scoreboard: Turtle
    _stats: dict[str, type]
    
    def __init__(self,
                 stats: dict[str, type], 
                 scoreboard: Turtle):
        dirname, _ = setup_db_dir(scoreboard)
        # print(dirname)
        self.dbname = os.path.join(dirname, "stats.sqlite")
        # print(self.dbname)
        self._scoreboard = scoreboard
        self._stats = stats
        for statname in stats:
            try:
                getattr(scoreboard, statname)
            except:
                raise ValueError("Each key in the stats dictionary must be the name of an attribute of the scoreboard.")
        make_stats_db(stats, self.dbname)
        self.con = None  # filled in when calling with_connection methods
        # create the database if there isn't one already.
        # add an index on filenames to speed searches.
        num_vals = 2 + len(self._stats)
        colnames = "(username, date, " + ", ".join(self._stats) + ")"
        questionmarks = ", ".join("?" for ii in range(num_vals))
        self.insert_query = f"INSERT INTO stats {colnames} VALUES ({questionmarks})"
        # yeah, it sucks to be using f-strings in a SQL execute statement
        # but given that stats is a private variable and they have to be
        # the names of attributes of the scoreboard, it's likely fine

    @property
    def stats(self):
        return self._stats.copy()

    @with_connection
    def all(self) -> list:
        '''all rows from the database'''
        return self.con.execute("SELECT * FROM stats").fetchall()

    @with_connection
    def all_by_user(self, username: str) -> list:
        '''get all rows for a given username'''
        return self.con.execute(
            "SELECT * FROM stats WHERE username = ?", (username,)
        ).fetchall()
    
    @with_connection
    def all_on_date(self, date: datetime.date) -> list:
        '''get all rows on a given date'''
        return self.con.execute(
            "SELECT * FROM stats WHERE date = ?", (date,)
        ).fetchall()

    @with_connection
    def by_user_on_date(self, username: str, date: datetime.date) -> list:
        '''get all rows on a given date for a given username'''
        return self.con.execute(
            "SELECT * FROM stats WHERE username = ? AND date = ?", 
            (username, date)
        ).fetchall()

    @with_connection
    def top_by_stat(self, statname: str, top: int = 1) -> list:
        '''get all rows with the all-time highest values of statname
        across all users'''
        return self.con.execute(
            f"SELECT * FROM stats ORDER BY {statname} DESC LIMIT ?", 
            (top,)
        ).fetchall()

    @with_connection
    def top_by_stat_on_date(self, date: datetime.date, statname: str, top: int = 1) -> list:
        '''all rows with the top values of statname on a given date'''
        return self.con.execute(
            f"SELECT * FROM stats WHERE date = ? ORDER BY {statname} DESC LIMIT ?", 
            (date, top)
        ).fetchall()

    @with_connection
    def top_by_stat_by_user(self, username: str, statname: str, top: int = 1) -> list:
        '''all rows with the top values of statname for a given username'''
        return self.con.execute(
            f"SELECT * FROM stats WHERE username = ? ORDER BY {statname} DESC LIMIT ?", 
            (username, top)
        ).fetchall()
    
    @with_connection
    def top_by_stat_by_user_on_date(self, username: str, date: datetime.date, statname: str, top: int = 1) -> list:
        '''all rows with the top values of statname for a given username on a given date'''
        return self.con.execute(
            f"SELECT * FROM stats WHERE username = ? AND date = ? ORDER BY {statname} DESC LIMIT ?", 
            (username, date, top)
        ).fetchall()

    @with_connection
    def first_per_date(self, statname: str, first_day: datetime.date) -> list:
        """the highest score and the person who got that score for each day
        since first_day"""
        query = f'''
SELECT mud.username, mud.date, mud.mx 
FROM ( -- get max value per username by date
    SELECT username, date, MAX({statname}) mx
    FROM stats
    WHERE date >= ?
    GROUP BY username, date
    ) mud 
JOIN ( -- get highest overall score per day
    SELECT date, MAX({statname}) mx
    FROM stats
    WHERE date >= ?
    GROUP BY date
    ) md
WHERE mud.date = md.date AND mud.mx = md.mx
ORDER BY mud.date
LIMIT 1
        '''
        return self.con.execute(query, 
            (first_day, first_day)
        ).fetchall()

    @with_connection
    def execute(self, query):
        out = self.con.execute(query)
        return out.fetchall()

    @with_connection
    def store(self, username: str) -> None:
        '''get the current values of each stat of interest from the
        scoreboard, and then add a new row to the database with
        the username, today's date, and each stat.'''
        today = datetime.date.today()
        values = [username, today]
        for statname in self._stats:
            # get the current value of each stat from the scoreboard
            values.append(getattr(self._scoreboard, statname))
        # print(f"writing values {values}")
        self.con.execute(self.insert_query, values)
