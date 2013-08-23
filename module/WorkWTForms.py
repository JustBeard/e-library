#!/usr/bin/env python

from wtforms import Form, TextField, SelectMultipleField, PasswordField,\
                validators

class SearchBooksForm(Form):
    search_by_title = TextField('Title', [validators.Length(max=100, 
                                message="Search word is very large (Title)")])
    search_by_author = TextField('Author', [validators.Length(max=50, 
                                message="Search word is very large (Author)")])

class AddAuthorForm(Form):
    name = TextField("Name author", [validators.Length(min=2, max=50,
                message="Incorrect length of the field: min=2 and max=50 chars")])

class AddBookForm(Form):
    title = TextField("Title of the book", [validators.Length(min=1, max=100,
                message="Incorrect length of the field (Title): min=1 and max=100 chars")])
    choose_authors = SelectMultipleField("Authors of the book", coerce=int)

    def validate_choose_authors(form, field):
        if len(field.data) < 1:
            raise validators.ValidationError('You must select authors')

class LoginForm(Form):
    username = TextField("Username", [validators.Length(min=5, max=30,
                message="Incorrect length of the username: min=5 and max=30 chars")])
    password = PasswordField("Password", [validators.Length(min=5, max=100,
                message="Incorrect length of the password: min=5 and max=100 chars")])

class RegistrationForm(Form):
    username = TextField("Username", [validators.Length(min=5, max=30, 
                message="Incorrect length of the username: min=5 and max=30 chars")])
    password = PasswordField("Password", [validators.Length(min=5, max=100,
                message="Incorrect length of the password: min=5 and max=100 chars"),
                validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField("Repeat password", [validators.Length(min=5, max=100,
                message="Incorrect length of the password: min=5 and max=100 chars")])