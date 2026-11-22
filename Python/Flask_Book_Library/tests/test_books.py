import unittest

from sqlalchemy.exc import IntegrityError

from project import app, db
from project.books.models import Book


class TestBook(unittest.TestCase):
    def setUp(self):
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()
        Book.query.delete()
        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        Book.query.delete()
        db.session.commit()
        db.session.remove()
        self.ctx.pop()

    def add_book(self, name="Pan Tadeusz", year=1834):
        book = Book(name, "Adam Mickiewicz", year, "5days")
        db.session.add(book)
        db.session.commit()
        return book

    # poprawne dane
    def test_valid_book_is_saved(self):
        self.add_book()
        book = Book.query.first()
        self.assertEqual(book.name, "Pan Tadeusz")
        self.assertEqual(book.author, "Adam Mickiewicz")
        self.assertEqual(book.year_published, 1834)
        self.assertEqual(book.status, "available")

    def test_repr_contains_fields(self):
        text = repr(self.add_book())
        self.assertIn("Pan Tadeusz", text)
        self.assertIn("Adam Mickiewicz", text)

    # niepoprawne dane
    def test_missing_argument_raises(self):
        with self.assertRaises(TypeError):
            Book(name="Tylko tytuł")

    def test_duplicate_name_rejected(self):
        self.add_book()
        with self.assertRaises(IntegrityError):
            self.add_book()

    # wstrzyknięcie SQL
    def test_sql_injection_does_not_break_table(self):
        payload = "Robert'); DROP TABLE books;--"
        self.add_book(name=payload)
        self.assertEqual(Book.query.count(), 1)
        self.assertEqual(Book.query.first().name, payload)

    # wstrzyknięcie JavaScript
    def test_javascript_is_rejected(self):
        with self.assertRaises(ValueError):
            self.add_book(name="<script>alert('xss')</script>")

    # dane ekstremalne
    def test_very_long_name_is_rejected(self):
        with self.assertRaises(ValueError):
            self.add_book(name="A" * 5000)

    def test_negative_year_is_rejected(self):
        with self.assertRaises(ValueError):
            self.add_book(year=-100)


if __name__ == "__main__":
    unittest.main()
