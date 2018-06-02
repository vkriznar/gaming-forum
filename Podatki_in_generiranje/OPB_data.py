import pandas
import csv
import numpy as np
import random
import psycopg2
import psycopg2.extensions
import psycopg2.extras
import hashlib
import auth as auth
from bottle import *
# Povezovanje na bazo#
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)  # se znebimo problemov s šumniki
# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)  # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
# poženemo strežnik na portu 8080, glej http://localhost:8080/
# run(host='localhost', port=8080, reloader=True)

# Slovarji za lažje urejanje

Jeziki = {1: 'Slovensko', 2: 'Angleško', 3: 'Nemško', 4: 'Italjansko', 5: 'Francosko', 6: 'Špansko'}
Igre = {1: 'Runescape', 2: 'Chess', 3: 'Skyrim', 4: 'Fornite',
        5: 'Super Mario', 6: 'PlayerUnknown''s Battlegrounds'}
Platforme = {1: 'PC', 2: 'Playstation 4', 3: 'XBOX One', 4: 'Nintendo Switch'}
# Klani = {1: 'Marijani', 2: 'Divjaki', 3: 'Bratovščina sinjega galeba',
#          4: 'Gams in pivo'}  # Koliko klanov?
# za vsako igro tabela vlog.
Vloge = {1: 'Skiller', 2: 'Pker', 3: 'PvMer', 4: 'Team player',
         5: 'Solo player', 6: 'Speed runner', 7: 'Casual player', 8: 'Explorer', 9: 'Novice', 10: 'Expert', 11: 'National Master', 12: 'International Master', 13: 'Grandmaster'}
Vloge_v_igri = {1: [1, 2, 3], 2: [9, 10, 11, 12, 13],
                3: [6, 8, 7], 4: [4, 5], 5: [6, 7],
                6: [5, 4]}  # morava dodat se vloge v bazo?
Opcije_komunikacije = {1: 'Skype', 2: 'Discord', 3: 'Teamspeak'}  # katere opcije komunikacije?
# To, katera igra je katere zvrsti in katere vloge so v kateri igri bova pac morala peš nrdit, ostalo lahko generirava.
Zvrst = {1: 'MMORPG', 2: 'Strategy', 3: 'RPG', 4: 'TPS', 5: 'Arcade', 6: 'FPS'}
Zvrsti_v_igrah = {'Runescape': 'MMORPG', 'Chess': 'Strategy', 'Skyrim': 'RPG',
                  'Fornite': 'TPS', 'Super Mario': 'Arcade', 'PlayerUnknown''s Battlegrounds': 'FPS'}
Na_Platformi = {1: [1], 2: [1, 2, 3], 3: [1, 2, 3, 4],
                4: [1, 2, 3], 5: [1, 4], 6: [1, 2, 3]}

stevilo_uporabnikov = 1000


# def hash(string): za zahashat?
#    return fn(string)
#

osebe_in = open("osebe_data.csv")
racuni_in = open("racuni_data.csv")
osebe = csv.reader(osebe_in)
next(osebe, None)
racuni = csv.reader(racuni_in)
next(racuni, None)


def hashano_geslo(s):
    h = hashlib.md5()
    h.update(s.encode('utf-8'))
    return h.hexdigest()


# vstavljenje v osebe
for rows in osebe:
    cur.execute('INSERT INTO oseba(ime_oseba, priimek_oseba, casovni_pas) VALUES ( %s, %s, %s)', [
                rows[0], rows[1], rows[2]])

# vstavljenje v račune
for rows in racuni:
    cur.execute('INSERT INTO racun(uporabnisko_ime, id_lastnik, geslo_hash) VALUES (%s, %s, %s)', [
                rows[0], rows[1], hashano_geslo(rows[2])])

# vstavljanje v zvrsti
for k, v in Zvrst.items():
    cur.execute('INSERT INTO zvrst(id_zvrst, ime_zvrst) VALUES (%s, %s)', [k, v])

# vstavljanje v Vloge

for k, v in Vloge.items():
    cur.execute('INSERT INTO vloga(id_vloga, ime_vloga) VALUES (%s, %s)', [k, v])

# vstavljanje v igralec

for k, v in Igre.items():
    cur.execute('INSERT INTO igra(id_igra, ime_igra, zvrst) VALUES (%s, %s, %s)', [k, v, k])

# vstavljanje v ima_vlogo

for k, v in Vloge_v_igri.items():
    for j in v:
        cur.execute('INSERT INTO ima_vlogo(igra, vloga) VALUES (%s, %s)', [k, j])

# vstavljanja v platforma

for k, v in Platforme.items():
    cur.execute('INSERT INTO platforma(id_platforma, ime_platforma) VALUES (%s, %s)', [k, v])

# vstavljanje v na_platformi

for k, v in Na_Platformi.items():
    for j in v:
        cur.execute('INSERT INTO na_platformi(igra, platforma) VALUES (%s, %s)', [k, j])

# vstavljanje v jeziki

for k, v in Jeziki.items():
    cur.execute('INSERT INTO jezik(id_jezik, ime_jezik) VALUES (%s, %s)', [k, v])

# vstavljanje v opicje_komunikacije

for k, v in Opcije_komunikacije.items():
    cur.execute(
        'INSERT INTO opcija_komunikacije(id_komunikacija, ime_komunikacija) VALUES (%s, %s)', [k, v])


# vstavljanje v komunikator

for i in range(1, stevilo_uporabnikov + 1):
    for k, v in Opcije_komunikacije.items():
        if bool(random.getrandbits(1)):
            cur.execute(
                'INSERT INTO komunikator(komunikator, opcija_kom) VALUES (%s, %s)', [i, k])

# vstavljanje v govorec

for i in range(1, stevilo_uporabnikov + 1):
    for k, v in Jeziki.items():
        if bool(random.getrandbits(1)):
            cur.execute(
                'INSERT INTO govorec(govorec, jezik) VALUES (%s, %s)', [i, k])

# vstavljanje v igralec

for i in range(1, stevilo_uporabnikov + 1):
    for k, v in Igre.items():
        if bool(random.getrandbits(1)):
            vloga = random.randint(1, len(Vloge_v_igri[k]))
            platforma = random.randint(1, 4)
            cur.execute(
                'INSERT INTO igralec(igralec, igra, vloga, platforma) VALUES (%s, %s, %s, %s)', [i, k, vloga, platforma])
