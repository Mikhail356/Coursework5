import sqlite3
# from tqdm import tqdm

DATABASE = 'database.sqlite3'


def stemmer(lastname):
    return (lastname[:-1] if lastname[-1] == 'а' else lastname)


def check_name():
    names = []
    with sqlite3.connect(DATABASE) as connection:
        connection.create_function("stem", 1, stemmer)
        cursor = connection.cursor()
        # names =
        cursor.execute(
            'select stem(lastname) from man;'
        ).fetchall()
        # print(names)
        try:
            cursor.execute('drop table texts;')
            cursor.execute('drop table names;')
        except:
            pass
        cursor.execute(
            "CREATE VIRTUAL TABLE texts USING fts5(id, cont);")
        cursor.execute(
            "CREATE VIRTUAL TABLE names USING fts5(id, lastname, cont_id);")
        cursor.execute(
            "INSERT INTO texts (id, cont) Select id, cont from content;")
        cursor.execute(
            "INSERT INTO names (id, lastname) Select id, stem(lastname) from man;")
        print(cursor.execute(
            "select count(*) from texts;"
        ).fetchall())
        print(cursor.execute(
            "select count(*) from names;"
        ).fetchall())
        cursor.execute(
            'insert into match(cont_id, name_id) '
            + 'select texts.id, names.id from names, texts '
            + 'where texts.cont match(names.lastname);')  # limit 100
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
