"""
Test search in content alldb.sqlite3 the person 'Сергеев Александр Михайлович'
"""
import sqlite3
fio = 'Сергеев Александр Михайлович'
fio = fio.split()
reg_expr = (
    "({surname})|((({name[0]}|{name}).+)&(({patronymic[0]}|{patronymic}).+))"
).format(surname=fio[0], name=fio[1], patronymic=fio[2])
