from pathlib import Path
import pytz
import sqlite3

pwd = Path(__file__).parent

def get_banner_list(server: str):
    con = sqlite3.connect((pwd / f"../../gacha_data/gacha_data.db").as_posix())
    cur = con.cursor()