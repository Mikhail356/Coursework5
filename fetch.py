import sqlite3
import cdx_toolkit
from time import time
import bs4
from readability import Document


def get_data(db: str) -> None:
    con = sqlite3.connect(db)
    cur = con.cursor()
    url = cur.execute(
        """SELECT id, url FROM queue 
           WHERE load_started IS NULL 
           LIMIT 1""").fetchone()
    cdx = cdx_toolkit.CDXFetcher(source='cc')
    while url:
        url = cur.execute(
            """UPDATE queue SET load_started = current_timestamp
            FROM (SELECT id FROM queue WHERE load_started IS NULL LIMIT 1) FREE
            WHERE queue.id = free.id
            RETURNING queue.id, queue.url""").fetchone()
        if not url:
            break
        id_ = url[0]
        url = url[1]
        print(url)  # last update may be useless
        con.commit()
        for obj in cdx.iter(url, from_ts='202011', to='2020',
                            filter=['=status:200']):
            doc = Document(obj.content)
            soup = bs4.BeautifulSoup(doc.summary(), 'html.parser')
            cur.execute(
                """INSERT INTO content(url, raw_cont) VALUES (?, ?) 
                """, (obj['url'], soup.text))
            con.commit()
        cur.execute(
            """UPDATE queue SET load_complete = ? 
                WHERE id = ?""", (time(), id_))
    con.commit()
    con.close()
    return


if __name__ == '__main__':
    db = 'alldb.sqlite3'
    get_data(db)
