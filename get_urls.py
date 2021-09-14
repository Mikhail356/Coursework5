import bs4
import json
import requests
import sys
from multiprocessing.dummy import Pool, Queue
from tqdm import tqdm
"""
Functions to collect urls for websites in mass_media.txt
"""


def process_sites(url, api_url):
    pass


def process_sites_wrapper(i):
    index = requests.get('https://index.commoncrawl.org/collinfo.json').json()
    api_url = index[0]['cdx-api']
    while not queue.empty():
        url = queue.get()
        try:
            record = process_sites(url, api_url)
        except Exception as e:
            with lock:
                print(url, e, file=sys.stderr)
            record = dict()

        record_str = json.dumps(record, ensure_ascii=False)
        print(record_str, file=f_json)

        # счетчик должен атомарно обновиться
        with lock:
            pbar.update(1)


if __name__ == '__main__':
    with open('mass_media.txt', 'r') as file:
        url = file.read().split('\n')
    url.pop()
    queue = Queue()  # for collection urls on news websites
    for link in url:
        queue.put(link)

    with Pool(processes=4) as pool, tqdm(total=queue.qsize()) as pbar:
        lock = pbar.get_lock()
        pool.map(process_sites_wrapper, range(pool._process))
