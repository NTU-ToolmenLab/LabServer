DROP TABLE IF EXISTS login;
CREATE TABLE login (
  name TEXT PRIMARY KEY,
  pass TEXT NOT NULL
);

DROP TABLE IF EXISTS tokens;
CREATE TABLE tokens (
  tokenname TEXT PRIMARY KEY,
  tokenip   TEXT NOT NULL,
  name      TEXT NOT NULL,
  boxid     TEXT NOT NULL,
  boxname   TEXT NOT NULL,
  time      NUMERIC NOT NULL
);
