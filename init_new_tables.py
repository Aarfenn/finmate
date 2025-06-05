import sqlite3

conn = sqlite3.connect('users.db')
c = conn.cursor()

# Tabela kategorii
c.execute('''
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    color TEXT NOT NULL,
    monthly_limit REAL NOT NULL,
    UNIQUE(user_id, name),
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

# Tabela wydatków
c.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    budget_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(budget_id) REFERENCES budgets(id),
    FOREIGN KEY(category_id) REFERENCES categories(id)
)
''')

conn.commit()
conn.close()

print("Tabele 'categories' i 'expenses' zostały utworzone.")
