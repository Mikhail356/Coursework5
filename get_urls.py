import bs4
import re
import json
import requests
import sys
import zlib

from multiprocessing.dummy import Pool, Queue
from tqdm import tqdm
"""
Functions to collect urls for websites in mass_media.txt
"""


def process_sites(url, api_url, reg_expr):
    ans = []
    r = requests.get(api_url,
                     params={
                         'url': url+'*',
                         'limit': 3,
                         'output': 'json',
                         'filter': ['=status:200',
                                    '=language:rus' or '=language:rus,eng',
                                    ]
                     })
    records = [json.loads(line) for line in r.text.split('\n') if line]
    for record in records:
        if 'No Captures found' in record['message']:
            ans.append('No capture on cc for ' + url)
            continue
        prefix_url = 'https://commoncrawl.s3.amazonaws.com/'
        data_url = prefix_url + record['filename']
        start_byte = int(record['offset'])
        end_byte = start_byte + int(record['length'])
        headers = {'Range': f'bytes={start_byte}-{end_byte}'}
        r = requests.get(data_url, headers=headers)
        data = zlib.decompress(r.content, wbits=zlib.MAX_WBITS | 16)
        try:
            soap = bs4.BeautifulSoup(data.decode('utf-8'), 'html.parser')
            res = re.search('{}'.format(reg_expr), soap.text)
        except:
            ans.append('err_in_analyze ' + url)
            continue
        if res != None:
            ans.append(url)
    return ans


def process_sites_wrapper(i):
    index = requests.get('https://index.commoncrawl.org/collinfo.json').json()
    api_url = index[0]['cdx-api']
    fio = 'Сергеев Александр Михайлович'
    fio = fio.split()
    reg_expr = '({surname})|((({name[0]}|{name}).+)&(({patronymic[0]}|{patronymic}).+))'.format(
        surname=fio[0], name=fio[1], patronymic=fio[2])
    with open('data/part_{}.txt'.format(i), 'w') as file:
        while not queue.empty():
            url = queue.get()
            '''
            try:
                record = process_sites(url, api_url, reg_expr)
            except Exception as e:
                with lock:
                    print(url, e, file=sys.stderr)
                record = 'skip ' + url'''
            record = process_sites(url, api_url, reg_expr)
            for string in record:
                file.write(str(string)+'\n')

            # счетчик должен атомарно обновиться
            with lock:
                pbar.update(1)


if __name__ == '__main__':
    with open('mass_media.txt', 'r') as file:
        url = file.read().split('\n')
    url.pop()
    queue = Queue()  # for collection urls on news websites
    for link in url:
        queue.put(link+'*')

    with Pool(processes=1) as pool, tqdm(total=queue.qsize()) as pbar:
        lock = pbar.get_lock()
        pool.map(process_sites_wrapper, range(pool._processes))
