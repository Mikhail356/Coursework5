import sqlite3
from tqdm import tqdm

NAMEBASE = 'db-names_sqlite3.sqlite3'
TEXTBASE = 'alldb.sqlite3'
GENINDEX = 'generate_fts_index'


def check_name():
    names = []
    with sqlite3.connect(TEXTBASE) as connection:
        with sqlite3.connect(NAMEBASE) as name_connection:
            cursor = name_connection.cursor()
            names = cursor.execute(
                'select lastname from man;'
            ).fetchall()
        names = ['"'+(i[0][:-1] if i[0][-1] ==
                      'а' else i[0]) + '"' for i in names]
        cursor = connection.cursor()
        # cursor.execute(
        #     "CREATE VIRTUAL TABLE texts USING fts5(id, cont);")
        # cursor.execute(
        #     "CREATE VIRTUAL TABLE names USING fts5(id, name, cont_id);")
        cursor.execute(
            "attach 'alldb.sqlite3' as db1;")
        cursor.execute(
            "attach 'db-names_sqlite3.sqlite3' as db2;")
        cursor.execute(
            "INSERT INTO texts (id, cont) Select id, raw_cont from db1.content;")
        # cursor.execute(
        #     "INSERT INTO names (id, name) Select id, lastname from db2.man;")
        print(cursor.execute(
            "select count(*) from texts;"
        ).fetchall())
        # print(cursor.execute(
        #     "select count(*) from names;"
        # ).fetchall())
        for i in tqdm(range(len(names))):
            texts_id = cursor.execute(
                "SELECT texts.id  FROM texts  WHERE texts.cont MATCH ?;", (
                    names[i],)
            ).fetchall()
            for j in range(len(names)):
                if j != i:
                    texts_id_j = cursor.execute(
                        "SELECT texts.id  FROM texts  WHERE texts.cont MATCH ?;", (
                            names[j],)
                    ).fetchall()
                    tmp = list(set(texts_id) & set(texts_id_j))
            # if(len(tmp) > 0):
            #     print(names[i], names[j], tmp,
            #           texts_id, texts_id_j, sep='\n')

        #     cursor.execute(
        #         "INSERT INTO names (cont_id) VALUES (?);", (texts_id[0],))
        # with open('res.txt', 'w') as file:
        #     file.write(print(cursor.execute(
        #         "select * from names;"
        #     ).fetchall()))
        # cursor.execute(
        #     "DROP TABLE texts;")


check_name()
