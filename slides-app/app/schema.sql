DROP TABLE IF EXISTS user;
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

DROP TABLE IF EXISTS presentations;
CREATE TABLE presentations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    author_id INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (author_id) REFERENCES user (id) ON DELETE CASCADE
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
