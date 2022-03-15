import sqlite3
from tqdm import tqdm

DATABASE = 'database.sqlite3'


def check_name():
    names = []
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        names = cursor.execute(
            'select lastname, id from man;'
        ).fetchall()
        names = [('"'+(i[0][:-1] if i[0][-1] ==
                       'а' else i[0]) + '"', i[1]) for i in names]
        # print(names[:10])
        # cursor.execute("DROP TABLE texts;")
        # cursor.execute("DROP TABLE names;")
        cursor.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS texts USING fts5(id, cont);")
        cursor.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS names USING fts5(id, lastname, cont_id);")
        if cursor.execute('select count(*) from texts;').fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO texts (id, cont) Select id, cont from content;")
        # cursor.execute(
        #     "INSERT INTO names (id, lastname) Select id, lastname from man;")
        # print(cursor.execute(
        #     "select count(*) from texts;"
        # ).fetchall())
        # print(cursor.execute(
        #     "select count(*) from names;"
        # ).fetchall())
        # Filling nametext matching
        if(cursor.execute("select count(*) from nametext").fetchone()[0] == 0):
            for i in tqdm(range(len(names))):
                cursor.execute(
                    "INSERT INTO nametext(cont_id, name_id) SELECT * FROM (SELECT texts.id  FROM texts  WHERE texts.cont MATCH ?) LEFT JOIN (SELECT id from man where id = ?)", (names[i][0], names[i][1]))
            connection.commit()
        # print(cursor.execute("select count(*) from nametext").fetchone())
        for i in tqdm(range(len(names))):
            texts_id = cursor.execute(
                "SELECT texts.id  FROM texts  WHERE texts.cont MATCH ?;", (
                    names[i][0],)
            ).fetchall()
            rows = []
            for j in range(len(names)):
                if j != i:
                    texts_id_j = cursor.execute(
                        "SELECT texts.id  FROM texts  WHERE texts.cont MATCH ?;", (
                            names[j][0],)
                    ).fetchall()
                    texts = list(set(texts_id) & set(texts_id_j))
                    rows += [(names[i][1], names[j][1], cont_id[0])
                             for cont_id in texts]
            cursor.executemany(
                "INSERT INTO namenamecont(name1, name2, cont_id) VALUES (?, ?, ?)", rows)
            # for j in range(len(names)):
            #     if j != i:
            #         texts_id_j = cursor.execute(
            #             "SELECT texts.id  FROM texts  WHERE texts.cont MATCH ?;", (
            #                 names[j][0],)
            #         ).fetchall()
            #         tmp = list(set(texts_id) & set(texts_id_j))

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
