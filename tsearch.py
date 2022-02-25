"""
Test search in content TEXTBASE the person from NAMEBASE
"""
import sqlite3
import sys

NAMEBASE = 'db-names_sqlite3.sqlite3'
TEXTBASE = 'alldb.sqlite3'


def comparison(compr_type, names, text):
    """
    Return a list of text indexes where there is the name
    """
    if compr_type == 'coefficient':
        for name in names:
            coef = len(name[0])-2
            # name = " ".join(name)
            name = name[0]
            # name = name.lower()
            lname = len(name)
            record_id = text[0]
            cur_text = text[2]
            # cur_text = cur_text.lower()
            id_list = []
            max = 0
            for i in range(0, len(cur_text)-lname):
                count = 0
                for j in range(lname):
                    if cur_text[i: i + lname][j] == name[j]:
                        count += 1
                if count > max:
                    max = count
            if max >= coef:
                id_list.append(record_id)
    return id_list


def check_name():
    ans = []
    with sqlite3.connect(NAMEBASE) as connection:
        cursor = connection.cursor()
        names = cursor.execute(
            'select lastname, firstname, middlename from man;'
        ).fetchall()

        with sqlite3.connect(TEXTBASE) as connection:
            cursor = connection.cursor()
            cur_len = cursor.execute(
                'select count(*) from content;'
            ).fetchone()[0]
            texts = cursor.execute(
                'select * from content;')
            print(cur_len)
            for _ in range(cur_len):
                print(_)
                ans += comparison('coefficient', names, texts.fetchone())
            print(ans)


check_name()
# with sqlite3.connect(NAMEBASE) as connection:
#     cursor = connection.cursor()
#     name = cursor.execute(
#         'select lastname, firstname, middlename from man;'
#     ).fetchall()
#     print(f'size in Mbyte {sys.getsizeof(name)/1024}')
#     print(name)
