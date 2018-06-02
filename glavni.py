from bottle import *
import auth_public as auth
import psycopg2, psycopg2.extensions, psycopg2.extras
import hashlib

#priklop na bazo
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) #da imamo lahko sumnike
baza = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
baza.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogocimo transakcije
cur = baza.cursor(cursor_factory=psycopg2.extras.DictCursor)

secret = "56 Od nékdej lepé so Ljubljanke slovele, al lepši od Urške bilo ni nobene 56"
static_directory = "./startbootstrap-modern-business-gh-pages"

#username: chenker0
#password: v1202y

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
    return template("registration.html")


@post("/login/")
def login_post():
    username = request.forms.username
    password = hashano_geslo(request.forms.password)
    c = baza.cursor()
    c.execute("SELECT * FROM racun WHERE uporabnisko_ime=%s AND geslo=%s", [username, password])
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
    igre = []
    ID = table_users[0]
    c.execute("""SELECT igraID FROM igralec
                        JOIN racun ON igralec.id_igralec=racun.id
                        WHERE racun.ID=%s""", [ID])
    for i in range(0, N):
        x = c.fetchone()
        if x is not None:
            if x[0] == i + 1:
                igre.append(True)
            else:
                igre.append(False)
        if len(igre) < i + 1:
            igre.append(False)
    return template("index.html", user=username, igre=igre)


@get("/index/kontakt/")
def kontakt():
    return template("kontakt.html")

run(host='localhost', port=8080)
