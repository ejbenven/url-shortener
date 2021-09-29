"""
Contains the function responsible for handling database queries, such as adding an entry,
removing an entry, checking if an entry already exists in the database.
"""

import threading
import heapq
import time
import string
import re
import random
import enum

import sqlite3
from sho.html_page_generators import (
    name_collision_page,
    new_mapping_page,
    incorrect_submission_page,
)


class FormData:
    def __init__(self, **kwargs):
        self.url = self._format_long_url(kwargs["URL"][0])
        self.seo = self._format_short_url(kwargs["SEO"][0])
        self.ttl = 0 if not kwargs["TTL"][0] else int(kwargs["TTL"][0])

    def _format_long_url(self, url):
        if not url:
            return ""
        # We make sure that the given url is absolute
        url = "http://" + url if re.match(r"https?:\/\/", url) is None else url

        return url

    def _format_short_url(self, url):
        if not url:
            return ""
        # When queried with a GET request, the short url will have / prepended to its name
        url = "/" + url

        return url


@enum.unique
class DataParsingResult(enum.Enum):
    INCORRECT_SUBMISSION = 1
    NAME_COLLISION = 2
    CORRECT_SUBMISSION = 3


handle_request_lock = threading.Lock()


def handle_request(formfields, db_path):
    """
    Given the field of a POST request, this function will generate a short url
    following the specification.
    This function is protected by a lock in order to avoid a race condition that
    could lead to the same entry being added twice
    """
    data = FormData(**formfields)

    with handle_request_lock:
        status = parse_data(data, db_path)

        if status == DataParsingResult.INCORRECT_SUBMISSION:
            return incorrect_submission_page()

        if status == DataParsingResult.NAME_COLLISION:
            return name_collision_page(data.seo)

        if not data.seo:
            short_url = generate_short_url(db_path)
        else:
            short_url = data.seo

        add_mapping(short_url, data.url, data.ttl, db_path)
        return new_mapping_page(short_url, data.url)


def parse_data(data, db_path):
    if not data.url:
        return DataParsingResult.INCORRECT_SUBMISSION

    if data.seo and get_entry(data.seo, db_path):
        return DataParsingResult.NAME_COLLISION

    return DataParsingResult.CORRECT_SUBMISSION


def initialize_db(db_path):
    con = sqlite3.connect(db_path)
    with con:
        con.execute(
            "CREATE TABLE IF NOT EXISTS mappings (short_url text, long_url text, end_time int)"
        )
        result = con.execute("SELECT * FROM mappings WHERE short_url = '/'")
        result = result.fetchall()
        if not result:
            con.execute("INSERT INTO mappings VALUES('/', '/index.html', -1)")
    con.close()


def generate_short_url(db_path):
    characters = string.ascii_letters + string.digits
    url = "/" + "".join(random.choices(characters, k=6))

    while get_entry(url, db_path):
        url = "/" + "".join(random.choices(characters, k=6))

    return url


def add_mapping(key, value, ttl, db_path):
    con = sqlite3.connect(db_path)
    with con:
        con.execute(
            "INSERT INTO mappings VALUES (?, ?, ?)",
            (key, value, -1 if ttl == 0 else time.time() + ttl),
        )
    con.close()


def delete_expired_urls(db_path):
    t = time.time()
    con = sqlite3.connect(db_path)
    with con:
        con.execute("DELETE FROM mappings WHERE end_time BETWEEN 0 AND (?)", (int(t),))
    con.close()


def get_entry(key, db_path):
    con = sqlite3.connect(db_path)
    result = con.execute(
        "SELECT * FROM mappings WHERE short_url = :url", {"url": key}
    ).fetchall()
    con.close()

    return "" if not result else result[0]


def get_long_url(key, db_path):
    entry = get_entry(key, db_path)
    return "" if not entry else entry[1]
