import sys
import os
import unittest
import sqlite3
import time

sys.path.append(os.path.abspath("../"))
import sho.urlmap as urlmap


class TestUrlmap(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_db.db"

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_initialize(self):
        urlmap.initialize_db(self.db_path)
        con = sqlite3.connect(self.db_path)
        values = con.execute("SELECT * FROM mappings").fetchall()
        self.assertEqual(values, [("/", "/index.html", -1)])

        urlmap.initialize_db(self.db_path)
        con = sqlite3.connect(self.db_path)
        values = con.execute("SELECT * FROM mappings").fetchall()
        self.assertEqual(values, [("/", "/index.html", -1)])

    def test_get_entry_exists(self):
        urlmap.initialize_db(self.db_path)
        self.assertEqual(("/", "/index.html", -1), urlmap.get_entry("/", self.db_path))

    def test_get_entry_missing(self):
        urlmap.initialize_db(self.db_path)
        self.assertEqual("", urlmap.get_entry("hello", self.db_path))

    def test_get_long_url_exists(self):
        urlmap.initialize_db(self.db_path)
        self.assertEqual("/index.html", urlmap.get_long_url("/", self.db_path))

    def test_get_long_url_missing(self):
        urlmap.initialize_db(self.db_path)
        self.assertEqual("", urlmap.get_long_url("hello", self.db_path))

    def add_mapping(self):
        urlmap.initialize_db(self.db_path)
        con = sqlite3.connect(self.db_path)
        with con:
            con.execute("INSERT INTO mappings VALUES ('good', 'morning', 12)")

        val = con.execute("SELECT * FROM mappings WHERE short_url = 'good'").fetchall()

        self.assertEqual(len(val), 1)
        self.assertEqual(val[0], ("good", "morning", 12))

    def test_delete_expired_url(self):
        urlmap.initialize_db(self.db_path)
        con = sqlite3.connect(self.db_path)
        with con:
            con.execute("INSERT INTO mappings VALUES ('good', 'morning', 120)")

        urlmap.delete_expired_urls(self.db_path)

        val = con.execute("SELECT * FROM mappings WHERE short_url = 'good'").fetchall()
        self.assertEqual(val, [])

    def test_delete_expired_url_no_expired(self):
        urlmap.initialize_db(self.db_path)
        con = sqlite3.connect(self.db_path)
        t = time.time() + 3600
        with con:
            con.execute("INSERT INTO mappings VALUES ('good', 'morning', ?)", (t,))

        urlmap.delete_expired_urls(self.db_path)

        val = con.execute("SELECT * FROM mappings WHERE short_url = 'good'").fetchall()
        self.assertEqual(val, [("good", "morning", t)])

    def test_parse_data_no_url(self):
        urlmap.initialize_db(self.db_path)
        formfields = {"URL": [""], "SEO": ["bonjour"], "TTL": [4]}
        data = urlmap.FormData(**formfields)

        self.assertEqual(
            urlmap.parse_data(data, self.db_path),
            urlmap.DataParsingResult.INCORRECT_SUBMISSION,
        )

    def test_parse_data_name_collision(self):
        urlmap.initialize_db(self.db_path)
        con = sqlite3.connect(self.db_path)
        with con:
            con.execute(
                "INSERT INTO mappings VALUES (?, ?, ?)",
                ("/bonjour", "http://hello", 12),
            )

        formfields = {"URL": ["hello"], "SEO": ["bonjour"], "TTL": [4]}
        data = urlmap.FormData(**formfields)

        self.assertEqual(
            urlmap.parse_data(data, self.db_path),
            urlmap.DataParsingResult.NAME_COLLISION,
        )

    def test_parse_data_correct_request(self):
        urlmap.initialize_db(self.db_path)
        formfields = {"URL": ["hello"], "SEO": ["bonjour"], "TTL": [4]}
        data = urlmap.FormData(**formfields)

        self.assertEqual(
            urlmap.parse_data(data, self.db_path),
            urlmap.DataParsingResult.CORRECT_SUBMISSION,
        )


if __name__ == "__main__":
    unittest.main()
