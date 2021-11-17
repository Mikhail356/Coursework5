import sqlite3
import cdx_toolkit
import bs4
from time import sleep
from readability import Document
from itertools import zip_longest


def grouper(iterable, n, fillvalue=None):
    "Collect data into non-overlapping fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') —> ABC DEF Gxx
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def save_batch(batch, id_, db):
    while True:
        # try:
        with sqlite3.connect(db) as connection:
            cursor = connection.cursor()
            for document in batch:
                # try:
                cursor.execute(
                    """INSERT INTO content(url, raw_cont) 
                    VALUES (:url, :summary) """, document)
                # print(id_, type(id_))
                cursor.execute("""UPDATE queue 
                    SET load_complete = current_timestamp 
                    WHERE id = ?""", (id_,))
                # except Exception as e:
                # print(document['url'], document['summary'][:10_000],
                #   sep='\n\n\n')
            connection.commit()
            size = cursor.execute("""
            SELECT page_count * page_size as size
            FROM pragma_page_count(), pragma_page_size()
            """).fetchone()
            print(f'{size/1048576} Mbyte')
            break
        # except Exception as e:
        #     print(e, id_)
        #     sleep(0.0001)


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
        url_ = url[1]
        cdx_iterator = cdx.iter(url_, from_ts='202011', to='202012',
                                filter=['=status:200'])
        processed = ({"url": doc['url'],
                      "summary":
                      str(bs4.BeautifulSoup(
                          Document(doc.content).summary(), 'html.parser').text)
                      } for doc in cdx_iterator
                     )
        for batch in grouper(processed, 100):
            save_batch(batch, id_, db)
    con.commit()
    con.close()
    return


if __name__ == '__main__':
    db = 'alldb.sqlite3'
    get_data(db)
