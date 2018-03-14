DROP TABLE IF EXISTS login;
CREATE TABLE login (
  name TEXT PRIMARY KEY,
  pass TEXT NOT NULL,
  time FLOAT NOT NULL,
);

DROP TABLE IF EXISTS tokens;
CREATE TABLE tokens (
  tokenname   TEXT PRIMARY KEY,
  user        TEXT NOT NULL,
  tokenip     TEXT,
  tokenstatus TEXT,
  boxid       TEXT,
  boxname     TEXT NOT NULL,
  boxstatus   TEXT
);
