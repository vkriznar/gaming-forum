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


CREATE TABLE oseba (
id_oseba SERIAL PRIMARY KEY,
ime_oseba TEXT NOT NULL,
priimek_oseba TEXT NOT NULL,
casovni_pas TEXT NOT NULL
);

CREATE TABLE racun (
id_racun SERIAL PRIMARY KEY,
uporabnisko_ime TEXT NOT NULL,
id_lastnik INTEGER UNIQUE NOT NULL REFERENCES oseba(id_oseba),
geslo_hash TEXT NOT NULL
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
-- CONSTRAINT igra_vloga CHECK(ima_vlogo(igra, vloga) IS NOT NULL),
-- CONSTRAINT igra_platforma CHECK(na_platformi(igra, platforma) IS NOT NULL)
);

CREATE TABLE govorec (
govorec INTEGER REFERENCES racun(id_racun),
jezik INTEGER REFERENCES jezik(id_jezik),
PRIMARY KEY(govorec, jezik)
);


GRANT ALL ON ALL TABLES IN SCHEMA public TO galb;
GRANT ALL ON ALL TABLES IN SCHEMA public TO vidk;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO galb WITH GRANT OPTION;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO vidk WITH GRANT OPTION;
GRANT CONNECT ON DATABASE sem2018_galb TO javnost;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO javnost;
