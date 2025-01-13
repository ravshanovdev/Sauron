import os
import sqlite3
import pytest
from pylord.orm import Database, Table, Column, ForeignKey


@pytest.fixture()
def Author():
    class Author(Table):
        name = Column(str)
        age = Column(int)

    return Author


@pytest.fixture()
def db():
    DB_PATH = "./test.db"
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    db = Database(DB_PATH)
    return db


@pytest.fixture()
def Book(Author):
    class Book(Table):
        title = Column(str)
        published = Column(bool)
        author = ForeignKey(Author)

    return Book


def test_create_db(db):
    assert isinstance(db.conn, sqlite3.Connection)
    assert db.tables == []


def test_table_definition(Author, Book):
    assert Author.name.type == str
    assert Book.author.table == Author

    assert Author.name.sql_type == "TEXT"
    assert Author.age.sql_type == "INTEGER"

    assert Book.title.sql_type == "TEXT"
    assert Book.published.sql_type == "INTEGER"


def test_create_tables(Author, Book, db):
    db.create(Author)
    db.create(Book)

    assert Author._get_create_sql() == "CREATE TABLE IF NOT EXISTS author (id INTEGER PRIMARY KEY AUTOINCREMENT, age INTEGER, name TEXT);"
    assert Book._get_create_sql() == "CREATE TABLE IF NOT EXISTS book (id INTEGER PRIMARY KEY AUTOINCREMENT, author_id INTEGER, published INTEGER, title TEXT);"

    for table in ("author", "book"):
        assert table in db.tables


def test_create_table_instances(db, Author):
    db.create(Author)

    john = Author(name="kamoliddin", age=21)

    assert john.name == "kamoliddin"
    assert john.age == 21
    assert john.id is None


def test_db_save(db, Author):
    db.create(Author)

    kimdur = Author(name="kimdur", age=45)

    db.save(kimdur)

    assert kimdur._get_insert_sql() == (
        "INSERT INTO author (age, name) VALUES (?, ?);",
        [45, "kimdur"]
    )

    assert kimdur.id == 1


def test_query_all_authors(db, Author):
    db.create(Author)

    kamol = Author(name="kamoliddin", age=45)
    kimdur = Author(name="kimdur", age=44)

    db.save(kamol)
    db.save(kimdur)

    authors = db.all(Author)
    print(str(authors))

    assert Author._get_select_all_sql() == (
        "SELECT id, age, name FROM author;",
        ["id", "age", 'name']

    )

    assert len(authors) == 2
    assert isinstance(authors[0], Author)
    assert isinstance(authors[1], Author)

    for author in authors:
        assert author.age in {45, 44}
        assert author.name in {"kamoliddin", "kimdur"}
        assert author.id in {1, 2}


def test_get_author(db, Author):
    db.create(Author)

    kimdur = Author(name="kimdur", age=44)
    db.save(kimdur)

    kimdur_from_db = db.get(Author, id=1)

    assert Author._get_select_by_id_sql(id=1) == (
        "SELECT id, age, name FROM author WHERE id = 1;",
        ['id', "age", 'name']
    )

    assert isinstance(kimdur_from_db, Author)
    assert kimdur_from_db.id == 1
    assert kimdur_from_db.age == 44
    assert kimdur_from_db.name == "kimdur"


# ishlagani yoq
def test_to_get_book(db, Book, Author):
    db.create(Book)
    db.create(Author)

    kimdur = Author(name="kimdur", age=44)
    sandur = Author(name="sandur", age=78)

    nimadur = Book(title="utkan kunlar", published=True, author=kimdur)
    mandur = Book(title="mandur kitobi", published=True, author=sandur)

    db.save(kimdur)
    db.save(sandur)
    db.save(nimadur)
    db.save(mandur)

    book_from_db = db.get(Book, 2)

    assert book_from_db.title == "mandur kitobi"
    assert book_from_db.author.id == 2
    assert book_from_db.author.name == "sandur"
    assert book_from_db.author.age == 78


def test_all_book(db, Author, Book):
    db.create(Book)
    db.create(Author)

    kimdur = Author(name="kimdur", age=44)
    sandur = Author(name="sandur", age=78)

    nimadur = Book(title="utkan kunlar", published=True, author=kimdur)
    mandur = Book(title="mandur kitobi", published=True, author=sandur)

    db.save(kimdur)
    db.save(sandur)
    db.save(nimadur)
    db.save(mandur)

    db_get_all_books = db.all(Book)
    assert len(db_get_all_books) == 2
    assert db_get_all_books[1].author.id == 2
    assert db_get_all_books[1].author.name == "sandur"


def test_update_author(db, Author):
    db.create(Author)

    kimdur = Author(name="kimdur", age=45)
    db.save(kimdur)

    kimdur.name = "sandur"
    kimdur.age = 78

    db.update(kimdur)

    kimdur_from_db = db.get(Author, id=1)

    assert kimdur_from_db.name == "sandur"
    assert kimdur_from_db.age == 78


def test_delete_author(db, Author):
    db.create(Author)

    kimdur = Author(name="kimdur", age=78)
    db.save(kimdur)

    db.delete(Author, id=1)

    with pytest.raises(Exception):
        db.get(Author, id=1)



