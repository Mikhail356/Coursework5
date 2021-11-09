import sqlite3
import cdx_toolkit
from time import sleep
from readability import Document


def get_data(db: str) -> None:
    con = sqlite3.connect(db)
    cur = con.cursor()
    url = cur.execute(
        """SELECT id, url FROM queue 
           WHERE load_started IS NULL 
           LIMIT 1""").fetchone()
    con.close()
    cdx = cdx_toolkit.CDXFetcher(source='cc')
    while url:
        con = sqlite3.connect(db)
        cur = con.cursor()
        url = cur.execute(
            """UPDATE queue SET load_started = current_timestamp
            FROM (SELECT id FROM queue WHERE load_started IS NULL LIMIT 1) free
            WHERE queue.id = free.id
            RETURNING queue.id, queue.url""").fetchone()
        con.commit()
        con.close()
        if not url:
            break
        id_ = url[0]
        url = url[1]
        doc = []
        for ind, obj in enumerate(cdx.iter(url, from_ts='202011', to='2020',
                                           filter=['=status:200'])):
            doc.append((obj['url'], Document(obj.content)))
            print(ind)
            if ind % 100 == 0 and ind > 0:
                con = sqlite3.connect(db)
                cur = con.cursor()
                while True:
                    try:
                        for i in doc:
                            cur.execute(
                                """INSERT INTO content(url, raw_cont) 
                                VALUES (?, ?) 
                                """, (i[0], i[1].summary()))
                            cur.execute("""UPDATE queue 
                                SET load_complete = current_timestamp 
                                WHERE id = ?""", (id_))
                        con.commit()
                        size = cur.execute("""
                        SELECT page_count * page_size as size 
                        FROM pragma_page_count(), pragma_page_size()
                        """).fetchone()
                        print(f'{size/1048576} Mbyte')
                        con.close()
                        break
                    except:
                        sleep(0.0001)
                    doc = []
        if len(doc) % 100 != 0:
            pass
    con.commit()
    con.close()
    return


if __name__ == '__main__':
    db = 'alldb.sqlite3'
    get_data(db)
