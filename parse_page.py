import Tests

import requests
import bs4
import re
import sys


def parse(req=[], fio='Сергеев Александр Михайлович'):
    """
    Input is array of url that need to check on intersection (req) and some name in full format (fio): Surname Name Patronymic
    """
    fio = fio.split()
    reg_expr = '({surname})|((({name[0]}|{name}).+)&(({patronymic[0]}|{patronymic}).+))'.format(
        surname=fio[0], name=fio[1], patronymic=fio[2])

    print(reg_expr)
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
