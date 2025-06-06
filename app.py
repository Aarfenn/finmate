from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from dotenv import load_dotenv

# Ładowanie klucza tajnego
load_dotenv()

app = Flask(__name__)

# Bazowe kategorie wydatków z przypisanym kolorem
PREDEFINED_CATEGORIES = [
    {'name': 'Jedzenie', 'color': '#28a745'},    # zielony
    {'name': 'Transport', 'color': '#007bff'},   # niebieski
    {'name': 'Rozrywka', 'color': '#6f42c1'},    # fioletowy
    {'name': 'Rachunki', 'color': '#fd7e14'},    # pomarańczowy
]

app.secret_key = os.getenv('SECRET_KEY')

# >----------------------------------------------   Funkcje pomocnicze   ---------------------------------------------<


def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_category_id(name, conn):
    row = conn.execute('SELECT id FROM categories WHERE name = ?', (name,)).fetchone()
    return row['id'] if row else None


# >----------------------------------------------   Funkcje pomocnicze   ---------------------------------------------<

# >-------------------------------------------   Trasa domyślna logowanie   ------------------------------------------<
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('dashboard'))
        else:
            flash('Nieprawidłowy e-mail lub hasło.')
            return redirect(url_for('index'))

    return render_template('login.html')


# >----------------------------------   Rejestracja przejście ze strony logowania   ----------------------------------<
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if len(password) < 6:
            flash('Hasło musi mieć co najmniej 6 znaków.')
            return redirect(url_for('register'))

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if user:
            conn.close()
            flash('Użytkownik z takim e-mailem już istnieje.')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                     (name, email, hashed_password))
        conn.commit()
        conn.close()

        flash('Rejestracja zakończona sukcesem. Zaloguj się.')
        return redirect(url_for('index'))

    return render_template('register.html')


# >------------------------------   Strona główna bosługująca kluczowe funkcjonalności   -----------------------------<
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Musisz się zalogować.')
        return redirect(url_for('index'))

    user_id = session['user_id']
    conn = get_db_connection()

    budgets = conn.execute(
        'SELECT * FROM budgets WHERE user_id = ? ORDER BY year DESC, month DESC',
        (user_id,)
    ).fetchall()

    selected_budget = budgets[0] if budgets else None
    category_data = []

    if selected_budget:
        for cat in PREDEFINED_CATEGORIES:
            limit_row = conn.execute(
                'SELECT limit_amount FROM category_limits WHERE budget_id = ? AND category_name = ?',
                (selected_budget['id'], cat['name'])
            ).fetchone()

            limit = limit_row['limit_amount'] if limit_row else 0

            spent_row = conn.execute(
                '''SELECT SUM(amount) as total FROM expenses
                   WHERE budget_id = ? AND user_id = ? AND category_id = ?''',
                (selected_budget['id'], user_id, get_category_id(cat['name'], conn))
            ).fetchone()

            spent = spent_row['total'] if spent_row['total'] else 0

            category_data.append({
                'name': cat['name'],
                'color': cat['color'],
                'limit': limit,
                'spent': spent
            })

    conn.close()

    return render_template(
        'dashboard.html',
        budgets=budgets,
        category_data=category_data,
        selected_budget=selected_budget,
        predefined_categories=PREDEFINED_CATEGORIES
    )


# >-------------------------   Obsługa wylogowania po wciśnięciu przycisku na dashboardzie   -------------------------<
@app.route('/logout')
def logout():
    session.clear()
    flash('Zostałeś wylogowany.')
    return redirect(url_for('index'))


# >-------------------------------   Obsługa przycisku dodawania budżetu do historii   -------------------------------<
@app.route('/create_budget', methods=['GET', 'POST'])
def create_budget():
    if 'user_id' not in session:
        flash('Musisz się zalogować.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        year = int(request.form['year'])
        month = int(request.form['month'])
        income = float(request.form['income'])

        conn = get_db_connection()
        existing = conn.execute(
            'SELECT id FROM budgets WHERE user_id = ? AND year = ? AND month = ?',
            (session['user_id'], year, month)
        ).fetchone()

        if existing:
            conn.execute(
                'UPDATE budgets SET income = ? WHERE id = ?',
                (income, existing['id'])
            )
        else:
            conn.execute(
                'INSERT INTO budgets (user_id, year, month, income) VALUES (?, ?, ?, ?)',
                (session['user_id'], year, month, income)
            )

        conn.commit()
        conn.close()

        flash('Budżet zapisany pomyślnie.')
        return redirect(url_for('dashboard'))

    return render_template('create_budget.html')


# >-------------------------------------------   Dodanie wydatku do listy   ------------------------------------------<
@app.route('/add_expense', methods=['POST'])
def add_expense():
    if 'user_id' not in session:
        flash("Zaloguj się, aby dodać wydatek.")
        return redirect(url_for('index'))

    user_id = session['user_id']
    category_name = request.form['category']
    amount = float(request.form['amount'])
    budget_id = int(request.form['budget_id'])

    conn = get_db_connection()
    category_id = get_category_id(category_name, conn)

    if category_id:
        conn.execute(
            'INSERT INTO expenses (user_id, budget_id, category_id, amount) VALUES (?, ?, ?, ?)',
            (user_id, budget_id, category_id, amount)
        )
        conn.commit()
        flash("Wydatek dodany.")
    else:
        flash("Nie znaleziono kategorii.")

    conn.close()
    return redirect(url_for('dashboard'))


# >-------------------------   Obsługa zmiany zawartości panelu podglądu wybranego budżetu   -------------------------<
@app.route('/dashboard/<int:budget_id>')
def dashboard_preview(budget_id):
    if 'user_id' not in session:
        flash('Musisz się zalogować.')
        return redirect(url_for('index'))

    user_id = session['user_id']
    conn = get_db_connection()

    budgets = conn.execute(
        'SELECT * FROM budgets WHERE user_id = ? ORDER BY year DESC, month DESC',
        (user_id,)
    ).fetchall()

    selected_budget = conn.execute(
        'SELECT * FROM budgets WHERE id = ? AND user_id = ?',
        (budget_id, user_id)
    ).fetchone()

    if not selected_budget:
        flash('Nie znaleziono budżetu.')
        return redirect(url_for('dashboard'))

    category_data = []
    for cat in PREDEFINED_CATEGORIES:
        limit_row = conn.execute(
            'SELECT limit_amount FROM category_limits WHERE budget_id = ? AND category_name = ?',
            (selected_budget['id'], cat['name'])
        ).fetchone()
        limit = limit_row['limit_amount'] if limit_row else 0

        spent_row = conn.execute(
            '''SELECT SUM(amount) as total FROM expenses
               WHERE budget_id = ? AND user_id = ? AND category_id = ?''',
            (selected_budget['id'], user_id, get_category_id(cat['name'], conn))
        ).fetchone()

        spent = spent_row['total'] if spent_row['total'] else 0

        category_data.append({
            'name': cat['name'],
            'color': cat['color'],
            'limit': limit,
            'spent': spent
        })

    conn.close()

    return render_template(
        'dashboard.html',
        budgets=budgets,
        category_data=category_data,
        selected_budget=selected_budget,
        predefined_categories=PREDEFINED_CATEGORIES
    )


# >-------------------------   Obsługa zmiany zawartości panelu podglądu wybranego budżetu   -------------------------<
@app.route('/set_limit', methods=['POST'])
def set_limit():
    if 'user_id' not in session:
        return {'success': False, 'message': 'Brak autoryzacji.'}, 401

    data = request.get_json()
    budget_id = data.get('budget_id')
    category_name = data.get('category_name')
    limit = float(data.get('limit'))

    conn = get_db_connection()
    existing = conn.execute(
        'SELECT id FROM category_limits WHERE budget_id = ? AND category_name = ?',
        (budget_id, category_name)
    ).fetchone()

    if existing:
        conn.execute(
            'UPDATE category_limits SET limit_amount = ? WHERE id = ?',
            (limit, existing['id'])
        )
    else:
        conn.execute(
            'INSERT INTO category_limits (budget_id, category_name, limit_amount) VALUES (?, ?, ?)',
            (budget_id, category_name, limit)
        )

    conn.commit()
    conn.close()

    return {'success': True}


if __name__ == '__main__':
    app.run(debug=True)
