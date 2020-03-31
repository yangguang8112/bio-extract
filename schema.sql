
DROP TABLE IF EXISTS paper;

CREATE TABLE paper (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  downloaded TEXT NOT NULL,
  paper_url TEXT,
  key_words TEXT,
  pdf_path TEXT,
  author TEXT,
  quote INTEGER,
  pubtime TEXT,
  ner_res TEXT NOT NULL
);
