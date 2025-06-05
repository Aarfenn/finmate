import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()


c.execute('''
CREATE TABLE IF NOT EXISTS category_limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    budget_id INTEGER NOT NULL,
    category_name TEXT NOT NULL,
    limit_amount REAL NOT NULL,
    UNIQUE(budget_id, category_name),
    FOREIGN KEY(budget_id) REFERENCES budgets(id)
)
''')

conn.commit()
conn.close()

print("Utworzono tabelę limitów")
