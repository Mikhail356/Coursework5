import Tests

import requests
import bs4
import re
import sys
import json
import zlib
import cdx_toolkit


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


def process_sites(url, api_url, reg_expr):  #
    ans = []
    r = requests.get(api_url,
                     params={
                         'url': url,
                         'output': 'json',
                         'limit': 20,
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
        #print(data, r.text, sep='\n\n\n')
        try:
            soap = bs4.BeautifulSoup(data.decode('utf-8'), 'html.parser')
            res = re.search('{}'.format(reg_expr), soap.text)
            if res != None:
                ans.append(url)
        except:
            ans.append('err_in_analyze ' + url)
    return ans


if __name__ == '__main__':
    url = 'https://ria.ru/*'
    cdx = cdx_toolkit.CDXFetcher(source='cc')
    file = open('testout.txt', 'w')
    for obj in cdx.iter(url, from_ts='202011', to='2020', limit=2,
                        filter='=status:200'):
        soup = bs4.BeautifulSoup(obj.content, 'html.parser')
        fio = 'Сергеев Александр Михайлович'.split()
        reg_expr = '({surname})|((({name[0]}|{name}).+)&(({patronymic[0]}|{patronymic}).+))'.format(
            surname=fio[0], name=fio[1], patronymic=fio[2])
        res = re.search('{}'.format(reg_expr), soup.text)
        if res != None:
            file.writelines(
                obj.data['url'] + '\ttimestamp = ' + obj.data['timestamp'] + '\n')
            file.writelines(soup.text + '\n')
        else:
            print('skip ' + obj.data['url'] +
                  '\ttimestamp = ' + obj.data['timestamp'])
    file.close()
