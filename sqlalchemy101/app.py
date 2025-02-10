from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

# 📌 Konfiguracja bazy danych (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Ścieżka do SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super_tajne_haslo'  # Klucz do CSRF

db = SQLAlchemy(app)  # Inicjalizacja SQLAlchemy
csrf = CSRFProtect(app)  # Ochrona CSRF

# 📌 Definicja modelu notatek (tabeli w bazie danych)
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

# 📌 Tworzymy bazę danych, jeśli nie istnieje
with app.app_context():
    db.create_all()

# 📌 Formularz dla notatek (zastępuje "ręczny" formularz)
class NoteForm(FlaskForm):
    title = StringField('Tytuł', validators=[DataRequired()])
    content = TextAreaField('Treść', validators=[DataRequired()])
    submit = SubmitField('Zapisz')

# 📌 Strona główna – lista notatek
@app.route('/')
def index():
    notes = Note.query.order_by(Note.date_created.desc()).all()
    form = FlaskForm()  # Dodajemy pusty formularz do CSRF
    return render_template('index.html', notes=notes, form=form)

# 📌 Dodawanie nowej notatki
@app.route('/add', methods=['GET', 'POST'])
def add_note():
    form = NoteForm()
    if form.validate_on_submit():
        new_note = Note(title=form.title.data, content=form.content.data)
        db.session.add(new_note)
        db.session.commit()
        flash('Notatka dodana!', 'success')
        return redirect(url_for('index'))
    return render_template('add_note.html', form=form)

# 📌 Edycja notatki
@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    form = NoteForm(obj=note)

    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data
        db.session.commit()
        flash('Notatka zaktualizowana!', 'info')
        return redirect(url_for('index'))

    return render_template('edit_note.html', form=form, note=note)

# 📌 Usuwanie notatki
@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    flash('Notatka usunięta!', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
