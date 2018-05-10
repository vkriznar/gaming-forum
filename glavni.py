from bottle import *
import auth_public as auth
import psycopg2, psycopg2.extensions, psycopg2.extras
import hashlib

#priklop na bazo
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) #da imamo lahko sumnike
baza = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
baza.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogocimo transakcije
cur = baza.cursor(cursor_factory=psycopg2.extras.DictCursor)

skrivnost = "56 Od nékdej lepé so Ljubljanke slovele, al lepši od Urške bilo ni nobene 56"

def hashano_geslo(s):
    """Vrni MD5 hash danega UTF-8 niza. Gesla vedno spravimo v bazo
       kodirana s to funkcijo."""
    h = hashlib.md5()
    h.update(s.encode('utf-8'))
    return h.hexdigest()

def get_user(auto_login = True, auto_redir=False):
    """Poglej cookie in ugotovi, kdo je prijavljeni uporabnik,
       vrni njegov username in ime. Ce ni prijavljen, presumeri
       na stran za prijavo ali vrni None (advisno od auto_login).
    """
    # Dobimo username iz piskotka
    username = request.get_cookie('username', secret=secret)
    # Preverimo, ali ta uporabnik obstaja
    if username is not None:
        if auto_redir:
            # Ce uporabnik ze prijavljen, ga damo na domačo stran
            redirect('/index/')
        else:
            c = baza.cursor()
            c.execute("SELECT username FROM uporabnik WHERE username=%s", [username])
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

@get("/login/")
def login_get():
    curuser = get_user(auto_login = False, auto_redir = True)
    return template("login.html", napaka=None, username=None)

@post("/login/")
def login_post():
    username = request.forms.username
    password = hashano_geslo(request.forms.password)
    c = baza.cursor()
    c.execute("SELECT * FROM uporabnik WHERE username=%s AND hash=%s", [username, password])
    table_users = c.fetchone()
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

run(host='localhost', port=8080, debug=True)
