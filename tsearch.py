"""
Test search in content TEXTBASE the person from NAMEBASE
Assumptions: 1.There are no mistakes in spelling the lastname.
"""
import sqlite3
import json
from tqdm import tqdm

NAMEBASE = 'db-names_sqlite3.sqlite3'
TEXTBASE = 'alldb.sqlite3'

TCHECK1 = "Хуснутдиновой Арбенин очень хорошие рабочие. Земцова новый участник ВАК. "
TCHECK2 = "Юрчук и Пономарев выиграли грант. Арбенин и ОРехов захватили лес в Сибири."
TCHECK3 = "Юрчук Арбенин и ОРех захватили лес в Сибири."


def comparison(compr_type, names, texts, name_list, start_id=0):
    """
    Return a list of text indexes where there is the name
    """
    if compr_type == 'simple':
        for ind, text in enumerate(texts):
            # print(start_id+ind)
            cur_text = text[0]  # [0]
            for ind_name, name in enumerate(names):
                if name in cur_text:
                    if ind_name not in name_list:
                        name_list[ind_name] = []
                    name_list[ind_name].append(start_id+ind)  # record_id
    return name_list


def check_name():
    ans = dict()
    names = 0
    with sqlite3.connect(NAMEBASE) as connection:
        cursor = connection.cursor()
        names = cursor.execute(
            'select lastname from man;'
        ).fetchall()
    names = [(i[0][:-1] if i[0][-1] == 'а' else i[0]) for i in names]

    with sqlite3.connect(TEXTBASE) as connection:
        cursor = connection.cursor()
        cur_len = cursor.execute(
            'select count(*) from content;'
        ).fetchone()[0]
        texts = cursor.execute(
            'select raw_cont from content;')
        # print(names[:10])
        for i in tqdm(range((cur_len//1000) + 1)):
            ans = comparison('simple', names, texts.fetchmany(1000),
                             ans, i*1000)

    with open('answer.txt', 'w') as file:
        file.write(json.dumps(ans))


# check_name()
# with sqlite3.connect(NAMEBASE) as connection:
#     cursor = connection.cursor()
#     name = cursor.execute(
#         'select lastname, firstname, middlename from man;'
#     ).fetchall()
#     print(f'size in Mbyte {sys.getsizeof(name)/1024}')
#     print(name)
