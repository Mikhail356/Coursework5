from time import sleep
import tqdm
import sqlite3


def complite(db: str) -> None:
    con = sqlite3.connect(db)
    cur = con.cursor()
    total_len = cur.execute("SELECT COUNT(*) FROM queue").fetchone()[0]
    pbar = tqdm.tqdm(total=total_len)
    cur_len = cur.execute(
        "SELECT COUNT(*) FROM queue WHERE load_started IS NOT NULL").fetchone()[0]
    pbar.update(cur_len)
    while total_len > cur_len:
        cur_new_len = cur.execute(
            "SELECT COUNT(*) FROM queue WHERE load_started IS NOT NULL").fetchone()[0]
        pbar.update(cur_new_len-cur_len)
        cur_len = cur_new_len
        sleep(1)
    con.close()
    return


if __name__ == '__main__':
    db = 'alldb.sqlite3'
    complite(db)
