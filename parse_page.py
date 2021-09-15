import Tests

import requests
import bs4
import re
import sys
import json
import zlib


def parse(req=[], fio='Сергеев Александр Михайлович'):
    """
    Input is array of url that need to check on intersection (req) and some name in full format (fio): Surname Name Patronymic
    """
    fio = fio.split()
    reg_expr = '({surname})|((({name[0]}|{name}).+)&(({patronymic[0]}|{patronymic}).+))'.format(
        surname=fio[0], name=fio[1], patronymic=fio[2])

    file = open('out.txt', 'w')
    for i in req:
        try:
            soap = bs4.BeautifulSoup(requests.get(i).text, 'html.parser')
        except:
            print(i+'\t not processed')
            continue
        res = re.search('{}'.format(reg_expr), soap.text)
        if res != None:
            file.writelines(soap.text)
            file.writelines('\^*^/'*100)
        else:
            print('skip '+i)


def process_sites(url, api_url, reg_expr):
    ans = []
    r = requests.get(api_url,
                     params={
                         'url': url,
                         'output': 'json',
                         'filter': '=status:200'
                     })
    records = [json.loads(line) for line in r.text.split('\n') if line]
    print(records[0].keys())
    for record in records:
        if 'message' in record.keys() and 'No Captures found' in record['message']:
            ans.append('No capture on cc for ' + url)
            continue
        prefix_url = 'https://commoncrawl.s3.amazonaws.com/'
        data_url = prefix_url + record['filename']
        start_byte = int(record['offset'])
        end_byte = start_byte + int(record['length'])
        headers = {'Range': f'bytes={start_byte}-{end_byte}'}
        r = requests.get(data_url, headers=headers)
        data = zlib.decompress(r.content, wbits=zlib.MAX_WBITS | 16)
        print(data, r.text, sep='\n\n\n')
        try:
            soap = bs4.BeautifulSoup(data.decode('utf-8'), 'html.parser')
            res = re.search('{}'.format(reg_expr), soap.text)
            if res != None:
                ans.append(url)
        except:
            ans.append('err_in_analyze ' + url)
    return ans


if __name__ == '__main__':
    index = requests.get('https://index.commoncrawl.org/collinfo.json').json()
    api_url = index[0]['cdx-api']
    fio = 'Сергеев Александр Михайлович'
    fio = fio.split()
    reg_expr = '({surname})|((({name[0]}|{name}).+)&(({patronymic[0]}|{patronymic}).+))'.format(
        surname=fio[0], name=fio[1], patronymic=fio[2])
    url = 'http://1mediainvest.ru/*'
    ans = process_sites(url, api_url, reg_expr)
    print(ans)
