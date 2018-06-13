from bottle import *
import auth as auth
import psycopg2, psycopg2.extensions, psycopg2.extras
import hashlib
import webbrowser

#priklop na bazo
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) #da imamo lahko sumnike
baza = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
baza.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogocimo transakcije
cur = baza.cursor(cursor_factory=psycopg2.extras.DictCursor)

secret = "56 Od nékdej lepé so Ljubljanke slovele, al lepši od Urške bilo ni nobene 56"
static_directory = "./startbootstrap-modern-business-gh-pages"

webbrowser.open('http://localhost:8080/login/')

"""Vsa gesla bodo za-hashana, pomozna funkcija za to"""
def hashano_geslo(s):
    h = hashlib.md5()
    h.update(s.encode('utf-8'))
    return h.hexdigest()


"""Dobimo uporabnika iz piskotka, ce ga ni, ga vrzemo na login stran"""
def get_user(auto_login = True, auto_redir=False):
    # Dobimo username iz piskotka
    username = request.get_cookie('username', secret=secret)
    # Preverimo, ali ta uporabnik obstaja
    if username is not None:
        if auto_redir:
            # Ce uporabnik ze prijavljen, ga damo na domačo stran
            redirect('/index/')
        else:
            c = baza.cursor()
            c.execute("SELECT uporabnisko_ime FROM racun WHERE uporabnisko_ime=%s", [username])
            r = c.fetchone()
            c.close ()
            if r is not None:
                # uporabnik obstaja, vrnemo njegove podatke
                return r
    # uporabnik ni prijavljen, vrnemo ga na login page
    if auto_login:
        redirect('/login/')
    else:
        return None

@route("/startbootstrap-modern-business-gh-pages/<filename:path>")
def static(filename):
    return static_file(filename, root=static_directory)

@get("/login/")
def login_get():
    curuser = get_user(auto_login = False, auto_redir = True)
    return template("login.html", napaka=None, username=None)

"""Route za registrirat"""
@get("/registration/")
def registration_get():
    return template("registration.html", napaka=None)

@post("/registration/")
def registration_post():
    username = request.forms.username
    password = hashano_geslo(request.forms.password)
    name = request.forms.name
    surname = request.forms.surname
    email = request.forms.email
    c = baza.cursor()
    if(username is not None and password is not None and name is not None and surname is not None and email is not None):
        c.execute("SELECT * FROM racun WHERE uporabnisko_ime=%s", [username])
        if c.fetchone() is not None:
            return template("registration.html", napaka="Uporabnik s tem uporabniškim imenom že obstaja")
        else:
            c.execute("SELECT * FROM oseba WHERE email=%s", [email])
            if c.fetchone() is not None:
                return template("registration.html", napaka="Ta email je že v uporabi")
            else:
                c.execute("SELECT COUNT(*) FROM racun")
                n = c.fetchone()
                print(n[0])
                c.execute("""INSERT INTO oseba (id_oseba, ime_oseba, priimek_oseba, email)
                                            VALUES (%s, %s, %s, %s)""", [n[0] + 1, name, surname, email])
                c.execute("""INSERT INTO racun (id_racun, uporabnisko_ime, id_lastnik, geslo_hash)
                                VALUES (%s, %s, %s, %s)""", [n[0]+1, username, n[0]+1, password])
                response.set_cookie('username', username, path='/', secret=secret)
                redirect('/registration/igre/')
    else:
        return template("registration.html", napaka="Vsa polja morajo biti izpolnjena")

@get("/registration/igre/")
def registration_igre():
    username = request.get_cookie('username', secret=secret)
    c = baza.cursor()
    c.execute("SELECT * FROM racun WHERE uporabnisko_ime=%s", [username])
    table_users = c.fetchone()
    N = 6  # Koliko je iger
    igre = [False, False, False, False, False, False]
    ID = table_users[0]
    c.execute("""SELECT igra FROM igralec
                                JOIN racun ON igralec.igralec=racun.id_racun
                                WHERE racun.id_racun=%s""", [ID])
    x = c.fetchone()
    while x is not None:
        for i in range(0, N):
            if not igre[i]:
                if x[0] == i + 1:
                    igre[i] = True
        x = c.fetchone()
    return template("registration_igre.html", user=username, igre=igre)



@post("/login/")
def login_post():
    username = request.forms.username
    password = hashano_geslo(request.forms.password)
    c = baza.cursor()
    c.execute("SELECT * FROM racun WHERE uporabnisko_ime=%s AND geslo_hash=%s", [username, password])
    table_users = c.fetchone()
    N = 6 #Koliko je iger
    if table_users is None:
        # Username in geslo se ne ujemata
        return template("login.html", napaka="Nepravilna prijava", username=username)
    else:
        response.set_cookie('username', username, path='/', secret=secret)
        redirect('/index/')


@get("/logout/")
def logout():
    response.delete_cookie('username', path='/', secret=secret)
    redirect('/login/')

@get("/index/")
def index():
    username = request.get_cookie('username', secret=secret)
    c = baza.cursor()
    c.execute("SELECT * FROM racun WHERE uporabnisko_ime=%s", [username])
    table_users = c.fetchone()
    N = 6  # Koliko je iger
    igre = [False, False, False, False, False, False]
    ID = table_users[0]
    c.execute("""SELECT igra FROM igralec
                        JOIN racun ON igralec.igralec=racun.id_racun
                        WHERE racun.id_racun=%s""", [ID])
    x = c.fetchone()
    while x is not None:
        for i in range(0, N):
            if not igre[i]:
                if x[0] == i+1:
                    igre[i] = True
        x = c.fetchone()
    return template("index.html", user=username, igre=igre)


@get("/index/kontakt/")
def kontakt():
    return template("kontakt.html")

@get("/index/sah/")
def sah():
    username = request.get_cookie('username', secret=secret)
    c = baza.cursor()
    c.execute("SELECT * FROM racun WHERE uporabnisko_ime=%s", [username])
    table_users = c.fetchone()
    N = 6  # Koliko je iger
    igre = [False, False, False, False, False, False]
    ID = table_users[0]
    c.execute("""SELECT igra FROM igralec
                            JOIN racun ON igralec.igralec=racun.id_racun
                            WHERE racun.id_racun=%s""", [ID])
    x = c.fetchone()
    while x is not None:
        for i in range(0, N):
            if not igre[i]:
                if x[0] == i + 1:
                    igre[i] = True
        x = c.fetchone()
    return template("sah.html", igre=igre)

@get("/index/sah/add/")
def add():
    username = request.get_cookie('username', secret=secret)
    c = baza.cursor()
    c.execute("SELECT id_racun FROM racun WHERE uporabnisko_ime=%s", [username])
    id = c.fetchone()[0]
    c.execute("""INSERT INTO igralec (igralec, igra, vloga, platforma)
                    VALUES (%s, 2, 9, 1)""", [id])
    redirect('/index/sah/')

@get("/index/runescape/")
def sah():
    username = request.get_cookie('username', secret=secret)
    c = baza.cursor()
    c.execute("SELECT * FROM racun WHERE uporabnisko_ime=%s", [username])
    table_users = c.fetchone()
    N = 6  # Koliko je iger
    igre = [False, False, False, False, False, False]
    ID = table_users[0]
    c.execute("""SELECT igra FROM igralec
                            JOIN racun ON igralec.igralec=racun.id_racun
                            WHERE racun.id_racun=%s""", [ID])
    x = c.fetchone()
    while x is not None:
        for i in range(0, N):
            if not igre[i]:
                if x[0] == i + 1:
                    igre[i] = True
        x = c.fetchone()
    return template("runescape.html", igre=igre)

@get("/index/runescape/add/")
def add():
    username = request.get_cookie('username', secret=secret)
    c = baza.cursor()
    c.execute("SELECT id_racun FROM racun WHERE uporabnisko_ime=%s", [username])
    id = c.fetchone()[0]
    c.execute("""INSERT INTO igralec (igralec, igra, vloga, platforma)
                    VALUES (%s, 1, 3, 1)""", [id])
    redirect('/index/runescape/')


@get("/index/fortnite/")
def sah():
    username = request.get_cookie('username', secret=secret)
    c = baza.cursor()
    c.execute("SELECT * FROM racun WHERE uporabnisko_ime=%s", [username])
    table_users = c.fetchone()
    N = 6  # Koliko je iger
    igre = [False, False, False, False, False, False]
    ID = table_users[0]
    c.execute("""SELECT igra FROM igralec
                            JOIN racun ON igralec.igralec=racun.id_racun
                            WHERE racun.id_racun=%s""", [ID])
    x = c.fetchone()
    while x is not None:
        for i in range(0, N):
            if not igre[i]:
                if x[0] == i + 1:
                    igre[i] = True
        x = c.fetchone()
    return template("fortnite.html", igre=igre)

@get("/index/fortnite/add/")
def add():
    username = request.get_cookie('username', secret=secret)
    c = baza.cursor()
    c.execute("SELECT id_racun FROM racun WHERE uporabnisko_ime=%s", [username])
    id = c.fetchone()[0]
    c.execute("""INSERT INTO igralec (igralec, igra, vloga, platforma)
                    VALUES (%s, 4, 4, 1)""", [id])
    redirect('/index/fortnite/')


@get("/index/skyrim/")
def sah():
    username = request.get_cookie('username', secret=secret)
    c = baza.cursor()
    c.execute("SELECT * FROM racun WHERE uporabnisko_ime=%s", [username])
    table_users = c.fetchone()
    N = 6  # Koliko je iger
    igre = [False, False, False, False, False, False]
    ID = table_users[0]
    c.execute("""SELECT igra FROM igralec
                            JOIN racun ON igralec.igralec=racun.id_racun
                            WHERE racun.id_racun=%s""", [ID])
    x = c.fetchone()
    while x is not None:
        for i in range(0, N):
            if not igre[i]:
                if x[0] == i + 1:
                    igre[i] = True
        x = c.fetchone()
    return template("skyrim.html", igre=igre)

@get("/index/skyrim/add/")
def add():
    username = request.get_cookie('username', secret=secret)
    c = baza.cursor()
    c.execute("SELECT id_racun FROM racun WHERE uporabnisko_ime=%s", [username])
    id = c.fetchone()[0]
    c.execute("""INSERT INTO igralec (igralec, igra, vloga, platforma)
                    VALUES (%s, 3, 7, 2)""", [id])
    redirect('/index/skyrim/')


@get("/index/pubg/")
def sah():
    username = request.get_cookie('username', secret=secret)
    c = baza.cursor()
    c.execute("SELECT * FROM racun WHERE uporabnisko_ime=%s", [username])
    table_users = c.fetchone()
    N = 6  # Koliko je iger
    igre = [False, False, False, False, False, False]
    ID = table_users[0]
    c.execute("""SELECT igra FROM igralec
                            JOIN racun ON igralec.igralec=racun.id_racun
                            WHERE racun.id_racun=%s""", [ID])
    x = c.fetchone()
    while x is not None:
        for i in range(0, N):
            if not igre[i]:
                if x[0] == i + 1:
                    igre[i] = True
        x = c.fetchone()
    return template("pubg.html", igre=igre)

@get("/index/pubg/add/")
def add():
    username = request.get_cookie('username', secret=secret)
    c = baza.cursor()
    c.execute("SELECT id_racun FROM racun WHERE uporabnisko_ime=%s", [username])
    id = c.fetchone()[0]
    c.execute("""INSERT INTO igralec (igralec, igra, vloga, platforma)
                    VALUES (%s, 6, 5, 3)""", [id])
    redirect('/index/pubg/')


@get("/index/supermario/")
def sah():
    username = request.get_cookie('username', secret=secret)
    c = baza.cursor()
    c.execute("SELECT * FROM racun WHERE uporabnisko_ime=%s", [username])
    table_users = c.fetchone()
    N = 6  # Koliko je iger
    igre = [False, False, False, False, False, False]
    ID = table_users[0]
    c.execute("""SELECT igra FROM igralec
                            JOIN racun ON igralec.igralec=racun.id_racun
                            WHERE racun.id_racun=%s""", [ID])
    x = c.fetchone()
    while x is not None:
        for i in range(0, N):
            if not igre[i]:
                if x[0] == i + 1:
                    igre[i] = True
        x = c.fetchone()
    return template("supermario.html", igre=igre)

@get("/index/supermario/add/")
def add():
    username = request.get_cookie('username', secret=secret)
    c = baza.cursor()
    c.execute("SELECT id_racun FROM racun WHERE uporabnisko_ime=%s", [username])
    id = c.fetchone()[0]
    c.execute("""INSERT INTO igralec (igralec, igra, vloga, platforma)
                    VALUES (%s, 5, 6, 1)""", [id])
    redirect('/index/supermario/')



@get("/registration/igre/sah/")
def add():
    username = request.get_cookie('username', secret=secret)
    c = baza.cursor()
    c.execute("SELECT id_racun FROM racun WHERE uporabnisko_ime=%s", [username])
    id = c.fetchone()[0]
    c.execute("""INSERT INTO igralec (igralec, igra, vloga, platforma)
                    VALUES (%s, 2, 9, 1)""", [id])
    redirect('/registration/igre/')


@get("/registration/igre/runescape/")
def add():
    username = request.get_cookie('username', secret=secret)
    c = baza.cursor()
    c.execute("SELECT id_racun FROM racun WHERE uporabnisko_ime=%s", [username])
    id = c.fetchone()[0]
    c.execute("""INSERT INTO igralec (igralec, igra, vloga, platforma)
                    VALUES (%s, 1, 3, 1)""", [id])
    redirect('/registration/igre/')


@get("/registration/igre/fortnite/")
def add():
    username = request.get_cookie('username', secret=secret)
    c = baza.cursor()
    c.execute("SELECT id_racun FROM racun WHERE uporabnisko_ime=%s", [username])
    id = c.fetchone()[0]
    c.execute("""INSERT INTO igralec (igralec, igra, vloga, platforma)
                    VALUES (%s, 4, 4, 1)""", [id])
    redirect('/registration/igre/')


@get("/registration/igre/skyrim/")
def add():
    username = request.get_cookie('username', secret=secret)
    c = baza.cursor()
    c.execute("SELECT id_racun FROM racun WHERE uporabnisko_ime=%s", [username])
    id = c.fetchone()[0]
    c.execute("""INSERT INTO igralec (igralec, igra, vloga, platforma)
                    VALUES (%s, 3, 7, 2)""", [id])
    redirect('/registration/igre/')


@get("/registration/igre/pubg/")
def add():
    username = request.get_cookie('username', secret=secret)
    c = baza.cursor()
    c.execute("SELECT id_racun FROM racun WHERE uporabnisko_ime=%s", [username])
    id = c.fetchone()[0]
    c.execute("""INSERT INTO igralec (igralec, igra, vloga, platforma)
                    VALUES (%s, 6, 5, 3)""", [id])
    redirect('/registration/igre/')

@get("/registration/igre/mario/")
def add():
    username = request.get_cookie('username', secret=secret)
    c = baza.cursor()
    c.execute("SELECT id_racun FROM racun WHERE uporabnisko_ime=%s", [username])
    id = c.fetchone()[0]
    c.execute("""INSERT INTO igralec (igralec, igra, vloga, platforma)
                    VALUES (%s, 5, 6, 1)""", [id])
    redirect('/registration/igre/')

run(host='localhost', port=8080)
