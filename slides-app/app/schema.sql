DROP TABLE IF EXISTS presentations;
CREATE TABLE presentations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    created_at TEXT DEFAULT (datetime('now','localtime'))
);

DROP TABLE IF EXISTS slides;
CREATE TABLE slides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    presentation_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    position INTEGER DEFAULT 0,
    image TEXT,
    FOREIGN KEY (presentation_id) REFERENCES presentations(id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS templates;
CREATE TABLE templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    layout TEXT NOT NULL
);
