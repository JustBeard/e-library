#!/usr/bin/env python

import sqlite3
from contextlib import closing
from sqlalchemy import create_engine, Table, Column, Integer, \
                    String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref, mapper, relation

engine = create_engine("sqlite:///db/e-lib.db")
Session = sessionmaker(bind=engine)
Base = declarative_base()

def init_db(schema, database, app):
    Base.metadata.create_all(engine)
    with closing(sqlite3.connect(database)) as db:
        with app.open_resource(schema) as f:
            db.cursor().executescript(f.read())
        db.commit()

Books_Authors = Table("books_authors", Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id")),
    Column("author_id", Integer, ForeignKey("authors.id"))
)

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key = True)
    title = Column(String(100), nullable = False)
    authors_by = relationship("Author", secondary = Books_Authors, backref = "books_by")

    def __init__(self, title):
        self.title = title

class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key = True)
    name = Column(String(50), nullable = False)

    def __init__(self, name):
        self.name = name

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True)
    username = Column(String(30), nullable = False)
    password = Column(String(100), nullable = False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

def get_all_books():
    my_session = Session()
    result = my_session.query(Book).order_by(Book.title)
    return result

def get_all_authors():
    my_session = Session()
    result = my_session.query(Author).order_by(Author.name)
    return result

def get_books(title, author):
    my_session = Session()
    result = my_session.query(Book).join(Book.authors_by, aliased=True)\
                        .filter(Book.title.contains(title))\
                        .filter(Author.name.contains(author))\
                        .order_by(Book.title)
    return result

def add_author(author):
    my_session = Session()
    my_session.add(Author(author))
    my_session.commit()

def get_author(id_author):
    my_session = Session()
    result = my_session.query(Author).filter(Author.id == id_author)
    return result[0]

def change_author(id_author, name):
    my_session = Session()
    count = my_session.query(Author).filter(Author.id == id_author)\
                .update({"name":name}, synchronize_session=False)
    if count == 1:
        my_session.commit()
        return True
    return False

def delete_author(id_author):
    my_session  =Session()
    count = my_session.query(Author).filter(Author.id == id_author)\
                .delete(synchronize_session=False)
    if count == 1:
        my_session.commit()
        return True
    return False

def get_book(id_book):
    my_session = Session()
    book = my_session.query(Book).filter(Book.id == id_book)
    return book[0]

def add_book(title, list_authors_id):
    my_session = Session()
    list_authors = my_session.query(Author).filter(Author.id.in_(list_authors_id))
    book = Book(title)
    book.authors_by = list(list_authors)
    my_session.add(book)
    my_session.commit()

def change_book(id_book, title, list_authors_id):
    my_session = Session()
    #list_authors = my_session.query(Author).filter(Author.id.in_(list_authors_id))
    count = my_session.query(Book).filter(Book.id == id_book)\
                    .update({"title":title}, synchronize_session=False)
    #edit_book.title = title
    #edit_book.authors_by = list(list_authors)
    my_session.commit()

def delete_book(id_book):
    my_session = Session()
    count = my_session.query(Book).filter(Book.id == id_book)\
                .delete(synchronize_session=False)
    if count == 1:
        my_session.commit()
        return True
    return False

def get_user(username):
    my_session = Session()
    user_db = my_session.query(User).filter(User.username == username).all()
    if len(user_db) == 1:
        return user_db[0]
    return False

def add_user(username, password):
    my_session = Session()
    user = User(username, password)
    my_session.add(user)
    my_session.commit()