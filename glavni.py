from bottle import *
import auth_public as auth
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

igre_podatki = {
    # (igra, vloga, platforma)
    'sah': (2, 9, 1),
    'runescape': (1, 3, 1),
    'fortnite': (4, 4, 1),
    'skyrim': (3, 7, 2),
    'pubg': (6, 5, 3),
    'supermario': (5, 6, 1),
}

igre_ime = ['rs', 'sah', 'sky', 'fort', 'mario', 'pubg']

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
            cur.execute("SELECT uporabnisko_ime FROM racun WHERE uporabnisko_ime=%s", [username])
            r = cur.fetchone()
            if r is not None:
                # uporabnik obstaja, vrnemo njegove podatke
                return r
    # uporabnik ni prijavljen, vrnemo ga na login page
    if auto_login:
        redirect('/login/')
    else:
        return None

def igra_igre(id):
    cur.execute("""SELECT igra FROM igralec
                            JOIN racun ON igralec.igralec=racun.id_racun
                            WHERE racun.id_racun=%s""", [id])
    return [igre_ime[igra-1] for igra, in cur]

@route("/startbootstrap-modern-business-gh-pages/<filename:path>")
def static(filename):
    return static_file(filename, root=static_directory)

@get("/")
def blank():
    redirect("/login/")

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
    if(username is not None and password is not None and name is not None and surname is not None and email is not None):
        cur.execute("SELECT * FROM racun WHERE uporabnisko_ime=%s", [username])
        if cur.fetchone() is not None:
            return template("registration.html", napaka="Uporabnik s tem uporabniškim imenom že obstaja")
        else:
            cur.execute("SELECT * FROM racun WHERE email=%s", [email])
            if cur.fetchone() is not None:
                return template("registration.html", napaka="Ta email je že v uporabi")
            else:
                cur.execute("""INSERT INTO racun (uporabnisko_ime, geslo_hash, ime_oseba, priimek_oseba, email)
                                VALUES (%s, %s, %s, %s, %s) RETURNING id_racun""", [username,  password, name, surname, email])
                response.set_cookie('username', username, path='/', secret=secret)
                redirect('/registration/igre/')
    else:
        return template("registration.html", napaka="Vsa polja morajo biti izpolnjena")

@get("/registration/igre/")
def registration_igre():
    username = request.get_cookie('username', secret=secret)
    cur.execute("SELECT * FROM racun WHERE uporabnisko_ime=%s", [username])
    table_users = cur.fetchone()
    id = table_users[0]
    igre = igra_igre(id)
    return template("registration_igre.html", user=username, igre=igre)



@post("/login/")
def login_post():
    username = request.forms.username
    password = hashano_geslo(request.forms.password)
    cur.execute("SELECT * FROM racun WHERE uporabnisko_ime=%s AND geslo_hash=%s", [username, password])
    table_users = cur.fetchone()
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
    cur.execute("SELECT * FROM racun WHERE uporabnisko_ime=%s", [username])
    table_users = cur.fetchone()
    id = table_users[0]
    igre = igra_igre(id)
    return template("index.html", user=username, igre=igre)


@get("/index/kontakt/")
def kontakt():
    return template("kontakt.html")

@get("/index/messenger/")
def messenger():
    username = request.get_cookie('username', secret=secret)
    cur.execute("""SELECT racun.uporabnisko_ime, sporocila.vsebina
                    FROM sporocila 
                    JOIN racun ON racun.id_racun=sporocila.posiljatelj
                    ORDER BY sporocila.datum ASC""")
    tmp = cur.fetchall()
    return template("messenger.html", rows=tmp, user=username)


@post("/index/messenger/")
def messenger_post():
    username = request.get_cookie('username', secret=secret)
    vsebina = request.forms.vsebina
    cur.execute("SELECT * FROM racun WHERE uporabnisko_ime=%s", [username])
    id = cur.fetchone()[0]
    if(vsebina is not ""):

        cur.execute("""INSERT INTO sporocila (posiljatelj, vsebina)
                        VALUES (%s, %s)""", [id, vsebina])
        redirect('/index/messenger/')
    else:
        cur.execute("""SELECT racun.uporabnisko_ime, sporocila.vsebina
                    FROM sporocila 
                    JOIN racun ON racun.id_racun=sporocila.posiljatelj
                    ORDER BY sporocila.datum ASC""")
        tmp = cur.fetchall()
        return template("messenger.html", rows=tmp, user=username)

@get("/index/<igra>/add")
def add(igra):
    igra_id, vloga, platforma = igre_podatki[igra]
    username = request.get_cookie('username', secret=secret)
    cur.execute("SELECT id_racun FROM racun WHERE uporabnisko_ime=%s", [username])
    id=cur.fetchone()[0]
    cur.execute("""INSERT INTO igralec (igralec, igra, vloga, platforma)
                    VALUES (%s, %s, %s, %s)""", [id, igra_id, vloga, platforma])
    baza.commit()
    redirect('/index/%s/' % igra)

@get("/index/<igra>/delete")
def add(igra):
    igra_id, vloga, platforma = igre_podatki[igra]
    username = request.get_cookie('username', secret=secret)
    cur.execute("SELECT id_racun FROM racun WHERE uporabnisko_ime=%s", [username])
    id=cur.fetchone()[0]
    cur.execute("DELETE FROM igralec WHERE igralec=%s AND igra=%s", [id, igra_id])
    baza.commit()
    redirect('/index/%s/' % igra)

@get("/registration/igre/<igra>/")
def add(igra):
    igra_id, vloga, platforma = igre_podatki[igra]
    username = request.get_cookie('username', secret=secret)
    cur.execute("SELECT id_racun FROM racun WHERE uporabnisko_ime=%s", [username])
    id=cur.fetchone()[0]
    cur.execute("""INSERT INTO igralec (igralec, igra, vloga, platforma)
                    VALUES (%s, %s, %s, %s)""", [id, igra_id, vloga, platforma])
    baza.commit()
    redirect('/registration/igre/')

@get("/index/<igra>/")
def igra(igra):
    username = request.get_cookie('username', secret=secret)
    cur.execute("SELECT * FROM racun WHERE uporabnisko_ime=%s", [username])
    table_users = cur.fetchone()
    id = table_users[0]
    igre = igra_igre(id)
    return template("%s.html" % igra, igre=igre)


run(host='localhost', port=8080)