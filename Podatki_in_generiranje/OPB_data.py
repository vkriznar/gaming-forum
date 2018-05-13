import pandas
import numpy as np
import random
Jeziki = {1: 'Slovene', 2: 'English', 3: 'German', 4: 'Italian', 5: 'French', 6: 'Spanish'}
Igre = {1: 'Runescape', 2: 'Chess', 3: 'Skyrim', 4: 'Fornite',
        5: 'Super Mario', 6: 'PlayerUnknown''s Battlegrounds'}
Platforme = {1: 'PC', 2: 'Playstation 4', 3: 'XBOX One', 4: 'Nintendo Switch'}
Klani = {}  # Koliko klanov?
# za vsako igro tabela vlog.
Vloge = {1: ['default'], 2: ['default'], 3: ['default'], 4: [],
         5: ['default'], 6: []}  # morava dodat se vloge v bazo?
Opcije_komunikacije = {}  # katere opcije komunikacije?
# To, katera igra je katere zvrsti in katere vloge so v kateri igri bova pac morala peš nrdit, ostalo lahko generirava.
Zvrst = {}

stevilo_uporabnikov = 1000


# def hash(string): za zahashat?
#    return fn(string)
#

randgen = np.random.randint(3, size=1000)
gms = []
for i in randgen:
    gms = np.append(gms, Igre[i])
gms
data = pandas.read_csv("/Users/Gal/Desktop/OPB/MOCK_DATA.csv")
data = data.assign(Games=gms)
data.to_csv("/Users/Gal/Desktop/OPB/test.csv", index=False)
data_test = pandas.read_csv("/Users/Gal/Desktop/OPB/test.csv")
data_test

# za generirange SQL stavkov za govorce
with open('govorci.txt', 'a') as govorci:
    for i in range(stevilo_uporabnikov):
        for k, v in Jeziki.items():
            if bool(random.getrandbits(1)):
                govorci.write('INSERT INTO govorec (id, id) VALUES (%d, %d);\n' % (i, k))

# generiranje SQL stavkov za igralce
with open('igralci.txt', 'a') as igralci:
    for i in range(stevilo_uporabnikov):
        for k, v in Igre.items():
            if bool(random.getrandbits(1)):
                nr = len(Vloge[k])
                st = random.randint(1, nr)
                platrand = random.randint(1, 4)
                igralci.write(
                    'INSERT INTO igralec (igralecid, igraid, vloga, platforma) VALUES (%d, %d, %d);\n' % (i, k, Vloge[k, st], platrand))

#  generiranje SQL stavkov za dodeljevanje v Klane, lahko dodava se opcijo da ni v klanu, treba se dopolnit s sevilom klanov.

with open('pripadniki.txt', 'a') as pripadniki:
    for i in range(stevilo_uporabnikov):
        pripadniki.write('INSERT INTO pripadnik (id, id) VALUES (%d, %d);\n' % (i, k))

# generiranje SQL stavkov za dodeljevanje moznosti komunikacije

with open('komunikator.txt', 'a') as komunikator:
    for i in range(stevilo_uporabnikov):
        for k, v in Opcije_komunikacije.items():
            if bool(random.getrandbits(1)):
                komunikator.write('INSERT INTO komunikator (id, id) VALUES (%d, %d);\n' % (i, k))
