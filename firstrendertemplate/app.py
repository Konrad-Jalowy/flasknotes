from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Funkcja pomocnicza do łączenia się z bazą danych
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Umożliwia odwoływanie się do kolumn po nazwie
    return conn

# Tworzenie tabeli, jeśli nie istnieje
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    print("Baza danych gotowa!")

init_db()  # Uruchamiamy tylko raz przy starcie aplikacji

# 📌 Strona główna – lista notatek
@app.route('/')
def index():
    conn = get_db_connection()
    notes = conn.execute('SELECT * FROM notes ORDER BY date_created DESC').fetchall()
    conn.close()
    return render_template('index.html', notes=notes)

# 📌 Dodawanie nowej notatki
@app.route('/add', methods=['GET', 'POST'])
def add_note():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        with get_db_connection() as conn:
            conn.execute('INSERT INTO notes (title, content) VALUES (?, ?)', (title, content))
        return redirect(url_for('index'))
    return render_template('add_note.html')

# 📌 Edycja notatki
@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    conn = get_db_connection()
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    conn.close()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        with get_db_connection() as conn:
            conn.execute('UPDATE notes SET title = ?, content = ? WHERE id = ?', (title, content, note_id))
        return redirect(url_for('index'))

    return render_template('edit_note.html', note=note)

# 📌 Usuwanie notatki
@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
