import sqlite3
import cdx_toolkit
from time import sleep
# import bs4
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
            FROM (SELECT id FROM queue WHERE load_started IS NULL LIMIT 1) free
            WHERE queue.id = free.id
            RETURNING queue.id, queue.url""").fetchone()
        con.commit()
        if not url:
            break
        id_ = url[0]
        url = url[1]
        for ind, obj in enumerate(cdx.iter(url, from_ts='202011', to='2020',
                                           filter=['=status:200'])):
            doc = Document(obj.content)
            print(ind)
            # soup = bs4.BeautifulSoup(doc.summary(), 'html.parser')
            while True:
                try:
                    cur.execute(
                        """INSERT INTO content(url, raw_cont) VALUES (?, ?) 
                        """, (obj['url'], doc.summary()))
                    # in place doc.summary() were soup.text
                    break
                except:
                    sleep(0.0001)
            if ind > 100:
                con.commit()
            while True:
                try:
                    cur.execute("""UPDATE queue 
                    SET load_complete = current_timestamp 
                    WHERE id = ?""", (id_))
                    break
                except:
                    sleep(0.0001)
            while True:
                try:
                    size = cur.execute("""SELECT page_count * page_size as 
                    size FROM pragma_page_count(), 
                    pragma_page_size()""").fetchone()
                    print(size)
                    break
                except:
                    sleep(0.0001)
    con.commit()
    con.close()
    return


if __name__ == '__main__':
    db = 'alldb.sqlite3'
    get_data(db)
