DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS otp_tokens;
DROP TABLE IF EXISTS password_reset_tokens;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    mfa_enabled INTEGER DEFAULT 0,
    mfa_secret TEXT
);

CREATE TABLE otp_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    used INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE TABLE password_reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    used INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
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
    bg_color TEXT DEFAULT '#ffffff',
    box_color TEXT DEFAULT NULL,
    title_font_size INTEGER DEFAULT 48,
    content_font_size INTEGER DEFAULT 20,
    FOREIGN KEY (presentation_id) REFERENCES presentations(id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS templates;
CREATE TABLE templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    layout TEXT NOT NULL
);
