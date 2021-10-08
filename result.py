import cdx_toolkit
import bs4
import re
from multiprocessing.dummy import Pool, Queue
from tqdm import tqdm


def process_sites(url, reg_expr):
    ans = []
    cdx = cdx_toolkit.CDXFetcher(source='cc')
    for obj in cdx.iter(url, from_ts='202011', to='2020', limit=2,
                        filter='=status:200'):
        soup = bs4.BeautifulSoup(obj.content, 'html.parser')
        res = re.search('{}'.format(reg_expr), soup.text)
        if res != None:
            ans.append(
                obj.data['url'] + '\ttimestamp = ' + obj.data['timestamp'] + '\n' + soup.text + '\n')
        else:
            ans.append('skip ' + obj.data['url'] +
                       '\ttimestamp = ' + obj.data['timestamp'])
    return ans

#    reg_expr = '({surname})|((({name[0]}|{name}).+)&(({patronymic[0]}|{patronymic}).+))'.format(
#        surname=fio[0], name=fio[1], patronymic=fio[2])


def process_sites_wrapper(i):
    fio = 'Сергеев Александр Михайлович'
    fio = fio.split()
    reg_expr = '{}'.format(fio[0])
    with open('data/part_{}.txt'.format(i), 'w') as file:
        while not queue.empty():
            url = queue.get()
            record = process_sites(url, reg_expr)
            for string in record:
                file.write(str(string)+'\n')

            # counter for tqdm
            with lock:
                pbar.update(1)


if __name__ == '__main__':
    with open('mass_media.txt', 'r') as file:
        url = file.read().split('\n')
    url.pop()
    queue = Queue()  # for collection urls on news websites
    reg = re.compile(r"https?://(www\.)?")
    for link in url:
        queue.put(reg.sub('', link).strip())

    with Pool(processes=4) as pool, tqdm(total=queue.qsize()) as pbar:
        lock = pbar.get_lock()
        pool.map(process_sites_wrapper, range(pool._processes))
