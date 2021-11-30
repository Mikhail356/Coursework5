"""Load text from CommonCrawl to content DATABASE by url in queue DATABASE"""

from time import sleep
import sqlite3
from itertools import zip_longest
from readability import Document
import cdx_toolkit
import bs4

DATABASE = 'alldb.sqlite3'


def grouper(iterable, chunk_len, fillvalue=None):
    """Collect data into non-overlapping fixed-length chunks or blocks"""
    # grouper('ABCDEFG', 3, 'x') —> ABC DEF Gxx
    args = [iter(iterable)] * chunk_len
    return zip_longest(*args, fillvalue=fillvalue)


def save_batch(batch, id_):
    """Uploads the finished data to the DATABASE content"""
    while True:
        with sqlite3.connect(DATABASE) as connection:
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


def get_summary(cdx_iterator):
    """
    return dict = {url:..., content:...} for write into DATABASE content
    or none
    """
    answer = dict()
    try:
        if cdx_iterator and len(cdx_iterator.content) > len('<html></html>'):
            answer['url'] = cdx_iterator['url']
            answer['summary'] = bs4.BeautifulSoup(
                Document(cdx_iterator.content).summary(), 'lxml'
            ).text
    except Exception as error:
        if cdx_iterator:
            print(1, cdx_iterator['url'], cdx_iterator.content, error,
                  sep='\n')
        else:
            print(2, cdx_iterator, error)
        return None
    return answer


def get_data() -> None:
    """Load data from common crawl and upload it to the content DATABASE"""
    url = ''
    cdx = cdx_toolkit.CDXFetcher(source='cc')
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        url = cursor.execute(
            """
            SELECT id, url FROM queue
            WHERE load_started IS NULL
            LIMIT 1""").fetchone()

    while url:
        with sqlite3.connect(DATABASE) as connection:
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
        id_, url_ = url[0], url[1]
        cdx_iterator = cdx.iter(url_, from_ts='202011', to='202012',
                                filter=['=status:200',
                                        '=mime-detected:text/html', ])
        processed = (
            {"url": summary['url'],
             "summary": summary['summary']
             } for summary in map(get_summary, cdx_iterator) if summary
        )
        for batch in grouper(processed, 100):
            save_batch(batch, id_)


if __name__ == '__main__':
    get_data()
