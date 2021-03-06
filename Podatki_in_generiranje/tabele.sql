DROP TABLE IF EXISTS oseba CASCADE;
DROP TABLE IF EXISTS racun CASCADE;
DROP TABLE IF EXISTS igra CASCADE;
DROP TABLE IF EXISTS platforma CASCADE;
DROP TABLE IF EXISTS na_platformi CASCADE;
DROP TABLE IF EXISTS jezik CASCADE;
DROP TABLE IF EXISTS zvrst CASCADE;
DROP TABLE IF EXISTS klan CASCADE;
DROP TABLE IF EXISTS opcija_komunikacije CASCADE;
DROP TABLE IF EXISTS komunikator CASCADE;
DROP TABLE IF EXISTS igralec CASCADE;
DROP TABLE IF EXISTS govorec CASCADE;
DROP TABLE IF EXISTS pripadnik CASCADE;
DROP TABLE IF EXISTS vloga CASCADE;
DROP TABLE IF EXISTS ima_vlogo CASCADE;
DROP TABLE IF EXISTS sporocila CASCADE;
DROP TABLE IF EXISTS clanek CASCADE;

CREATE TABLE racun (
id_racun SERIAL PRIMARY KEY,
uporabnisko_ime TEXT UNIQUE NOT NULL,
geslo_hash TEXT NOT NULL,
ime_oseba TEXT NOT NULL,
priimek_oseba TEXT NOT NULL,
email TEXT UNIQUE NOT NULL
);

CREATE TABLE zvrst (
id_zvrst INTEGER PRIMARY KEY,
ime_zvrst TEXT UNIQUE NOT NULL
);

CREATE TABLE vloga (
id_vloga INTEGER PRIMARY KEY,
ime_vloga TEXT NOT NULL
);


CREATE TABLE igra (
id_igra INTEGER PRIMARY KEY,
ime_igra TEXT NOT NULL,
zvrst INTEGER NOT NULL REFERENCES zvrst(id_zvrst)
);

CREATE TABLE ima_vlogo (
igra INTEGER REFERENCES igra(id_igra),
vloga INTEGER REFERENCES vloga(id_vloga),
PRIMARY KEY (igra, vloga)
);

CREATE TABLE platforma (
id_platforma INTEGER PRIMARY KEY,
ime_platforma TEXT UNIQUE NOT NULL
);

CREATE TABLE na_platformi (
igra INTEGER REFERENCES igra(id_igra),
platforma INTEGER REFERENCES platforma(id_platforma),
PRIMARY KEY (igra, platforma)
);

CREATE TABLE jezik (
id_jezik INTEGER PRIMARY KEY,
ime_jezik TEXT UNIQUE NOT NULL
);



CREATE TABLE opcija_komunikacije (
id_komunikacija INTEGER PRIMARY KEY,
ime_komunikacija TEXT UNIQUE NOT NULL
);

CREATE TABLE komunikator (
komunikator INTEGER REFERENCES racun(id_racun),
opcija_kom INTEGER REFERENCES opcija_komunikacije(id_komunikacija),
PRIMARY KEY(komunikator, opcija_kom)
);

CREATE TABLE igralec (
igralec INTEGER REFERENCES racun(id_racun),
igra INTEGER REFERENCES igra(id_igra),
vloga INTEGER REFERENCES vloga(id_vloga),
platforma INTEGER REFERENCES platforma(id_platforma),
PRIMARY KEY (igralec, igra, vloga, platforma),
FOREIGN KEY (igra, vloga) REFERENCES ima_vlogo(igra, vloga),
FOREIGN KEY (igra, platforma) REFERENCES na_platformi(igra, platforma)
);

CREATE TABLE govorec (
govorec INTEGER REFERENCES racun(id_racun),
jezik INTEGER REFERENCES jezik(id_jezik),
PRIMARY KEY(govorec, jezik)
);

CREATE TABLE clanek(
id_clanek SERIAL PRIMARY KEY,
naslov TEXT NOT NULL,
vsebina TEXT NOT NULL,
igra INTEGER REFERENCES igra(id_igra),
slika TEXT NOT NULL
);

CREATE TABLE sporocila(
id_sporocilo SERIAL PRIMARY KEY,
posiljatelj INTEGER REFERENCES racun(id_racun),
vsebina TEXT NOT NULL,
datum TIMESTAMP(0) DEFAULT now()
);

GRANT ALL ON ALL TABLES IN SCHEMA public TO galb;
GRANT ALL ON ALL TABLES IN SCHEMA public TO vidk;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO galb WITH GRANT OPTION;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO vidk WITH GRANT OPTION;
GRANT CONNECT ON DATABASE sem2018_galb TO javnost;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO javnost;
GRANT INSERT ON public.racun TO javnost;
GRANT INSERT ON public.sporocila TO javnost;
GRANT INSERT ON public.igralec TO javnost;
GRANT DELETE ON public.igralec TO javnost;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO javnost;
