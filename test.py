import cdx_toolkit
from tqdm import tqdm
import asyncio
import sqlite3
import time


async def complite(db: str) -> None:
    con = sqlite3.connect(db)
    cur = con.cursor()
    total_len = cur.execute("SELECT COUNT(*) FROM queue").fetchone()[0]
    pbar = tqdm(total=total_len)
    cur_len = cur.execute(
        "SELECT COUNT(*) FROM queue WHERE load_started IS NOT NULL").fetchone()[0]
    pbar.update(cur_len)
    while total_len > cur_len:
        cur_new_len = cur.execute(
            "SELECT COUNT(*) FROM queue WHERE load_started IS NOT NULL").fetchone()[0]
        pbar.update(cur_new_len-cur_len)
        cur_len = cur_new_len
        await time.sleep(1)
    con.close()
    return


async def get_raw_data(db: str) -> None:
    con = sqlite3.connect(db)
    cur = con.cursor()
    url = cur.execute(
        "SELECT id, url FROM queue WHERE load_started IS NULL LIMIT 1").fetchone()
    cdx = cdx_toolkit.CDXFetcher(source='cc')
    while url:
        url = cur.execute(
            "SELECT id, url FROM queue WHERE load_started IS NULL LIMIT 1").fetchone()
        id_ = url[0]
        url = url[1]
        cur.execute(
            "UPDATE queue SET load_started = {} WHERE id = {}".format
            (time.time(), id_)
        )
        con.commit()
        while(url):
            for obj in await cdx.iter(url, from_ts='202011', to='2020', limit=2,
                                      filter='=status:200'):
                cur.execute("INSERT INTO content(url, raw_cont) VALUES ({}, {}) WHERE".format(
                    obj['url'], obj.content))
            cur.execute(
                "UPDATE queue SET load_complete = {} WHERE id = {}".format
                (time.time(), id_)
            )
            con.commit()
    con.close()
    return


async def main(db: str) -> None:
    lst = []
    lst.append(complite(db))
    for _ in range(50):
        lst.append(get_raw_data(db))
    await asyncio.gather(*lst)


if __name__ == '__main__':
    db = 'alldb.sqlite3'
    asyncio.run(main(db))
