from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
import sqlite3
from datetime import datetime
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_tajne_haslo'  # Klucz do ochrony CSRF
csrf = CSRFProtect(app)  # Włączamy ochronę CSRF

# 📌 Formularz dla notatek (zabezpieczony CSRF)
class NoteForm(FlaskForm):
    title = StringField('Tytuł', validators=[DataRequired()])
    content = TextAreaField('Treść', validators=[DataRequired()])
    submit = SubmitField('Zapisz')

# 📌 Funkcja pomocnicza do łączenia się z bazą danych
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Możliwość odwoływania się do kolumn po nazwie
    return conn

# 📌 Tworzenie tabeli, jeśli nie istnieje
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
    
    form = FlaskForm()  # Dodajemy pusty formularz CSRF dla DELETE
    return render_template('index.html', notes=notes, form=form)


# 📌 Dodawanie nowej notatki
@app.route('/add', methods=['GET', 'POST'])
def add_note():
    form = NoteForm()  # Tworzymy formularz
    if form.validate_on_submit():  # Sprawdzamy, czy dane są poprawne
        title = form.title.data
        content = form.content.data
        with get_db_connection() as conn:
            conn.execute('INSERT INTO notes (title, content) VALUES (?, ?)', (title, content))
        flash('Notatka dodana!', 'success')
        return redirect(url_for('index'))
    return render_template('add_note.html', form=form)  # Przekazujemy form do szablonu

# 📌 Edycja notatki
@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    conn = get_db_connection()
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    conn.close()

    if not note:
        flash('Nie znaleziono notatki.', 'danger')
        return redirect(url_for('index'))

    form = NoteForm(data={'title': note['title'], 'content': note['content']})  # Wypełniamy formularz danymi

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        with get_db_connection() as conn:
            conn.execute('UPDATE notes SET title = ?, content = ? WHERE id = ?', (title, content, note_id))
        flash('Notatka zaktualizowana!', 'info')
        return redirect(url_for('index'))

    return render_template('edit_note.html', form=form)

# 📌 Usuwanie notatki
@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    flash('Notatka usunięta!', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
