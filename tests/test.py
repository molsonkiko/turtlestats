'''
run automated unit tests of turtlestats
'''
import time
import os
import sqlite3
import unittest

import pyautogui as pyag

from turtlestats.display import best_score_bar, top_users_bar, FIRST_UNIX_DAY

CODE_DIR = os.path.dirname(__file__)
TEST_GAME_STARTER = os.path.join(CODE_DIR, "start_test_game.bat")
STATS_DBNAME = os.path.join(CODE_DIR, '.turtlestats', 'stats.sqlite')

def play_game(username: str, ups: int, downs: int, dist_per_up = 0.5) -> bool:
    '''
    Play a round of the turtlestats test game with the designated number
    username, ups, downs, and dist_per_up.
    Return True if a congratulations window showed up, otherwise false
    '''
    assert ups + downs == 20
    os.startfile(TEST_GAME_STARTER)
    # can't use subprocess.run or subprocess.Popen
    # those block the calling thread until the process completes, so the
    # pyautogui stuff won't run until the game is over
    # wait for the window to open or bad things happen
    wnds = []
    while len(wnds) != 1:
        time.sleep(0.5)
        wnds = pyag.getWindowsWithTitle('User name')
    wnds[0].activate()
    for char in username:
        pyag.keyDown(char)
        pyag.keyUp(char)
        time.sleep(0.0125)
    pyag.keyDown('Enter')
    time.sleep(0.125)
    for char in str(dist_per_up):
        pyag.keyDown(char)
        pyag.keyUp(char)
        time.sleep(0.0125)
    pyag.keyDown('Enter')
    time.sleep(0.125)
    wnds = pyag.getWindowsWithTitle('Turtlestats test game')
    if len(wnds) != 1:
        raise FileNotFoundError("Should be exactly one window named 'Turtlestats test game'")
    wnds[0].activate()
    time.sleep(0.125)
    num_wnds_before = len(pyag.getAllWindows())
    # count how many windows there are before we play the game
    for ii in range(ups):
        pyag.keyDown('Up')
        pyag.keyUp('Up')
        time.sleep(0.0125)
    for ii in range(downs):
        pyag.keyDown('Down')
        pyag.keyUp('Down')
        time.sleep(0.0125)
    # now wait in case the congratulations message shows up
    time.sleep(0.25)
    # check if there are more windows after the game
    num_wnds_after = len(pyag.getAllWindows())
    if num_wnds_after > num_wnds_before:
        # if the message showed up, this will close the window
        pyag.keyDown('Enter')
    return num_wnds_after > num_wnds_before

ARGS_TO_ENTER = [ # username, ups, downs, distance_per_up, should congratulate
    ('mjo', 10, 10, 0.5, False),
    ('fnron', 12, 8, -0.5, False), # not a high score, don't congratulate
    ('mjo', 15, 5, 17, True), # highest score so far, so congrats!
    ('bozar', 12, 8, -1, False),
    ('bozar', 18, 2, 5, True), # highest score for bozar, but not overall
    ('norgurno', 0, 20, 20, False),
    ('anoru', 20, 0, -0.35, False),
    ('c2c', 20, 0, 0, False),
    ('mjo', 3, 17, -200, True), # new high score!
]

class Tester(unittest.TestCase):
    def test_1_add_rows(self):
        if os.path.exists(STATS_DBNAME):
            os.unlink(STATS_DBNAME)
        for args in ARGS_TO_ENTER:
            with self.subTest():
                congrats = play_game(*args[:-1])
                should_congratulate = args[-1]
                self.assertEqual(congrats, should_congratulate)

    def test_2_review_db(self):
        try:
            with sqlite3.connect(STATS_DBNAME) as con:
                con.row_factory = sqlite3.Row
                rows = con.execute("SELECT * FROM stats").fetchall()
        finally:
            con.close()
        for row, arg in zip(rows, ARGS_TO_ENTER):
            user, ups, downs = arg[:3]
            with self.subTest():
                self.assertEqual(user, row['username'])
            with self.subTest():
                self.assertEqual(ups, row['ups'])
            with self.subTest():
                self.assertEqual(downs, row['downs'])

    def test_3_top_users_bar_sql(self):
        try:
            with sqlite3.connect(STATS_DBNAME) as con:
                con.row_factory = sqlite3.Row
                rows = con.execute('''
SELECT * FROM
    (SELECT username, MAX(ups) mx 
    FROM stats GROUP BY username)
ORDER BY mx DESC
LIMIT ?
    ''',
                    (5,)
                ).fetchall()
        finally:
            con.close()
        with self.subTest():
            self.assertEqual(len(rows), 5)
        # want top 5 users
        with self.subTest():
            self.assertEqual(rows[0]['mx'], 20)
        with self.subTest():
            self.assertEqual(rows[2]['username'], 'bozar')
            # anoru and c2c are tied for most ups, bozar is 3rd
    
    def test_4_top_users_bar(self):
        top_users_bar('downs', 5, CODE_DIR, os.path.join(CODE_DIR, 'top_users_bar.png'))
        self.assertTrue(os.path.exists(os.path.join(CODE_DIR, 'top_users_bar.png')))

    def test_5_trend_bar_sql(self):
        try:
            with sqlite3.connect(STATS_DBNAME) as con:
                con.row_factory = sqlite3.Row
                rows = con.execute('''
SELECT date, mx FROM 
    (SELECT date, MAX(distance) mx 
    FROM stats GROUP BY date)
WHERE date > ?
ORDER BY date''',
                    (FIRST_UNIX_DAY,)
                ).fetchall()
        finally:
            con.close()
        self.assertEqual(len(rows), 1)
        # because all the rows were added the same day
        # unless the tests started just before midnight
        self.assertEqual(rows[0]['mx'], 2800)

    def test_6_trend_bar(self):
        best_score_bar('more_ups', FIRST_UNIX_DAY, CODE_DIR, os.path.join(CODE_DIR, 'more_ups_trend.png'))
        self.assertTrue(os.path.exists(os.path.join(CODE_DIR, 'more_ups_trend.png')))

    def test_7_teardown(self):
        os.unlink(STATS_DBNAME)
        os.rmdir(os.path.join(CODE_DIR, '.turtlestats'))
        os.unlink(os.path.join(CODE_DIR, 'top_users_bar.png'))
        os.unlink(os.path.join(CODE_DIR, 'more_ups_trend.png'))
        

if __name__ == '__main__':
    unittest.main(verbosity=2)