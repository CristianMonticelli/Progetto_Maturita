import os
import sqlite3

if not os.path.exists('instance'):
    os.makedirs('instance')

db_path = os.path.join('instance', 'slides.sqlite')
connection = sqlite3.connect(db_path)
with open('app/schema.sql', encoding='utf-8') as f:
    connection.executescript(f.read())
connection.commit()
connection.close()
print(f"Database creato in: {db_path}")
