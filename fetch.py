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
        with sqlite3.connect(db) as connection:
            cursor = connection.cursor()
            for document in batch:
                if isinstance(document, dict):
                    cursor.execute("""
                        INSERT INTO content(url, raw_cont) 
                        VALUES (:url, :summary)""", document)
                    cursor.execute("""
                        UPDATE queue 
                        SET load_complete = current_timestamp 
                        WHERE id = ?""", (id_,))
            connection.commit()
        break


def get_data(db: str) -> None:
    url = ''
    cdx = cdx_toolkit.CDXFetcher(source='cc')
    with sqlite3.connect(db) as connection:
        cursor = connection.cursor()
        url = cursor.execute(
            """
            SELECT id, url FROM queue 
            WHERE load_started IS NULL 
            LIMIT 1""").fetchone()

    while url:
        with sqlite3.connect(db) as connection:
            cursor = connection.cursor()
            size = cursor.execute("""
                SELECT page_count * page_size as size
                FROM pragma_page_count(), pragma_page_size()
                """).fetchone()
            print(f'{size[0]/1048576} Mbyte')
            if size[0]/1048576 > 5120:
                break
            url = cursor.execute("""
                UPDATE queue SET load_started = current_timestamp
                FROM 
                (SELECT id FROM queue WHERE load_started IS NULL LIMIT 1) free
                WHERE queue.id = free.id
                RETURNING queue.id, queue.url""").fetchone()
            connection.commit()
        if not url:
            break
        id_ = url[0]
        url_ = url[1]
        cdx_iterator = cdx.iter(url_, from_ts='202011', to='202012',
                                filter=['=status:200'])
        processed = ({"url": str(doc['url']),
                      "summary":
                      str(bs4.BeautifulSoup(
                          Document(doc.content).summary(), 'html.parser').text)
                      } for doc in cdx_iterator
                     )
        for batch in grouper(processed, 100):
            save_batch(batch, id_, db)


if __name__ == '__main__':
    db = 'alldb.sqlite3'
    get_data(db)
