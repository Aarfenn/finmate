import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    income REAL NOT NULL,
    UNIQUE(user_id, year, month)
)
''')

conn.commit()
conn.close()

print("Tabela 'budgets' została utworzona.")
