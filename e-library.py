#!/usr/bin/env python

import os
from flask import Flask, request, session, redirect, url_for, \
    abort, render_template, flash
import module.WorkSQLAlchemy as db_handler
import module.WorkWTForms as form_handler

DATABASE = 'db/e-lib.db'
PATH_DB_SCHEMA = 'db/schema.sql'
DEBUG = True
SECRET_KEY = 'development key'

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/', methods = ['GET', 'POST'])
def index():
    form = form_handler.SearchBooksForm(request.form)
    form_valid = form.validate()
    if request.method == "POST" and form_valid:
        books = db_handler.get_books(form.search_by_title.data, 
                                    form.search_by_author.data)
    else:
        books = db_handler.get_all_books()
        for field in form:
            for error in field.errors:
                flash(error)
        if not form_valid:
            form.search_by_title.data = ""
            form.search_by_author.data = ""
    return render_template("list_books.html", books = books, form=form)

@app.route('/add_author', methods = ['GET', 'POST'])
def add_author():
    if not session.get("logged"):
        abort(401)
    form = form_handler.AddAuthorForm(request.form)
    if request.method == "POST" and form.validate():
        db_handler.add_author(form.name.data)
        flash("New author save successfully")
        return redirect(url_for('index'))
    return render_template("add_author.html", form=form)

@app.route('/change_author/<int:author_id>', methods = ['GET', 'POST'])
def change_author(author_id):
    if not session.get("logged"):
        abort(401)
    if request.method != "POST":
        author = db_handler.get_author(author_id)
        form = form_handler.AddAuthorForm(name = author.name)
    else:
        form = form_handler.AddAuthorForm(request.form)
        if form.validate():
            if db_handler.change_author(author_id, form.name.data):
                flash("Changes author ({0}) save successfully".format(form.name.data))
                return redirect(url_for('index'))
        else:
            for field in form:
                for error in field.errors:
                    flash(error)
    return render_template("change_author.html", form=form, id = author_id)

@app.route('/delete_author/<int:author_id>')
def delete_author(author_id):
    if db_handler.delete_author(author_id):
        flash('The author successfully removed')
    return redirect(url_for('index'))

@app.route('/add_book', methods = ['GET', 'POST'])
def add_book():
    if not session.get("logged"):
        abort(401)
    form = form_handler.AddBookForm(request.form)
    authors = db_handler.get_all_authors()
    form.choose_authors.choices = [(g.id, g.name) for g in authors]
    if request.method == "POST" and form.validate():
        db_handler.add_book(form.title.data, form.choose_authors.data)
        flash("New book save successfully")
        return redirect(url_for('index'))
    else:
        for field in form:
            for error in field.errors:
                flash(error)
    return render_template("add_book.html", form=form)

@app.route('/change_book/<int:book_id>', methods = ['GET', 'POST'])
def change_book(book_id):
    if not session.get("logged"):
        abort(401)
    if request.method != "POST":
        book = db_handler.get_book(book_id)
        list_author_id = [author.id for author in book.authors_by]
        form = form_handler.AddBookForm(title = book.title, choose_authors = list_author_id)
    else:
        form = form_handler.AddBookForm(request.form)
    authors = db_handler.get_all_authors()
    form.choose_authors.choices = [(g.id, g.name) for g in authors]
    if request.method == "POST" and form.validate():
        db_handler.change_book(book_id, form.title.data, form.choose_authors.data)
        flash("Changes book ({0}) save successfully".format(form.title.data))
        return redirect(url_for('index'))
    elif request.method == "POST":
        for field in form:
            for error in field.errors:
                flash(error)
    return render_template("change_book.html", form=form, id=book_id)


@app.route('/delete_book/<int:book_id>', methods = ['GET', 'POST'])
def delete_book(book_id):
    if db_handler.delete_book(book_id):
        flash('The book successfully removed')
    return redirect(url_for('index'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = form_handler.LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = db_handler.get_user(form.username.data)
        if user:
            if form.password.data == user.password:
                session["logged"] = True
                flash("You was logged sucsesfully")
                return redirect(url_for('index'))
            else:
                flash("Wrong password")
        else:
            flash("Wrong username")
    else:
        for field in form:
            for error in field.errors:
                flash(error)
    return render_template("login.html", form=form)

@app.route('/logout')
def logout():
    session.pop("logged", None)
    flash("You were logged out")
    return redirect(url_for('index'))

@app.route('/registration', methods = ['GET', 'POST'])
def registration():
    form = form_handler.RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        db_handler.add_user(form.username.data, form.password.data)
        session["logged"] = True
        flash("You have successfully registered")
        return redirect(url_for('index'))
    else:
        for field in form:
            for error in field.errors:
                flash(error)
    return render_template('register.html', form=form)

if __name__ == "__main__":
    if not os.path.exists(app.config["DATABASE"]):
        db_handler.init_db(app.config["PATH_DB_SCHEMA"], app.config["DATABASE"], app)
    app.run()