from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from dotenv import load_dotenv

# Załaduj dane z pliku .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn


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


@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html')
    else:
        flash('Musisz się zalogować.')
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    flash('Zostałeś wylogowany.')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
