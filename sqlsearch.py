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
        count = 0
        intersect = 0
        for number in tqdm(range(len(texts_id))):
            text_id = texts_id[number]
            names = cursor.execute(
                "select id, lastname, firstname, middlename, expert from (select name_id from nametext where nametext.cont_id = ?) as name left join man on man.id = name.name_id;",
                (text_id[0],)).fetchall()
            # print(names)
            text = cursor.execute(
                "select cont, url from content where id = ?",
                (text_id[0],)
            ).fetchall()[0]
            url = text[1]
            text = text[0]
            lowtext = text.lower()
            intersect = 0
            for fullname in names:
                lastname = (
                    fullname[1][:-1] if fullname[1][-1] == 'а' else fullname[1]
                )
                name = (
                    fullname[2][:-1] if fullname[2][-1] == 'а' else fullname[2]
                )
                index1 = int(lowtext.find(lastname.lower()))
                index2 = int(lowtext[
                    max(index1-100, 0): min(index1+100, len(text))
                ].find(name.lower()))
                if index1 != -1 and index2 != -1:
                    intersect += 1
                    if intersect == 2:
                        count += 1
                        intersect = 0
                        break
                    # print('TEXT\n', text[:index1])
                    # print(text[index1:])
                    # print(fullname)
                    # print('LASTNAME INDEX', index1)
                    # print('NAME INDEX', max(index1+index2-100, 0))
                    # print('LEN TEXT', len(text))
                    # print('TEXT_ID', text_id)
                    # print('URL', text[1])
                    # input()
        print(count)


start_time = time()
check_nearby()
print("--- %s seconds ---" % (time() - start_time))
