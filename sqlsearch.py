import sqlite3
from time import time
from tqdm import tqdm

DATABASE = 'database.sqlite3'


def base_connection_with_names():
    """
    Creates and fills in tables that take into account 
    the relationship between surnames from the "man" table 
    and the contents from the "content" table, as well as 
    between surnames that exist in the same text from "content".

    All of the above is performed in the database DATABASE.
    """
    names = []
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()

        names = cursor.execute(
            'select lastname, id from man;'
        ).fetchall()
        names = [('"'+(i[0][:-1] if i[0][-1] ==
                       'а' else i[0]) + '"', i[1]) for i in names]

        cursor.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS texts USING fts5(id, cont);")
        cursor.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS names USING fts5(id, lastname, cont_id);")
        if cursor.execute('select count(*) from texts;').fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO texts (id, cont) Select id, cont from content;")

        # Filling nametext matching
        if(cursor.execute("select count(*) from nametext").fetchone()[0] == 0):
            for i in tqdm(range(len(names))):
                cursor.execute(
                    "INSERT INTO nametext(cont_id, name_id) SELECT texts.id cont_id, ? name_id FROM texts WHERE texts.cont MATCH ?", (names[i][1], names[i][0]))
        cursor.execute(
            "INSERT INTO namenamecont SELECT NULL id, n1.name_id name1, n2.name_id, n1.cont_id cont_id FROM nametext n1 JOIN nametext n2 ON n1.cont_id = n2.cont_id WHERE n1.name_id <> n2.name_id;"
        )
        connection.commit()


def check_nearby():
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        texts_id = cursor.execute(
            "SELECT distinct cont_id from namenamecont"
        ).fetchall()
        for text_id in texts_id:
            print(text_id)
            names = cursor.execute(
                "select id, lastname, firstname, middlename, expert from (select name_id from nametext where nametext.cont_id = ?) as name left join man on man.id = name.name_id;",
                (text_id[0],)).fetchall()
            print(names)
            text = cursor.execute(
                "select cont from content where id = ?",
                (text_id[0],)
            ).fetchall()[0]
            for name in names:
                print(name)
                name = name[1][:-1] if name[1][-1] == 'а' else name[1]
                index = int(text[0].find(name))
                print(text[0][max(index-50, 0): min(index+50, len(text[0]))])
            input()
            input()


start_time = time()
check_nearby()
print("--- %s seconds ---" % (time() - start_time))
