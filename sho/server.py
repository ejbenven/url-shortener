"""
This contains the setup logic for the service. It will create and initialize the database,
if needed, launch a thread responsible for deleting exired entries from the database, and
finally launch the webserver handling the customer's requests.
"""
import http.server
import argparse
import threading
import time

import sho.urlmap
import sho.request_handler


def thread_main(server_running, db_path):
    if server_running.is_set():
        sho.urlmap.delete_expired_urls(db_path)
        threading.Timer(10, thread_main, args=[server_running, db_path]).start()


def main():

    parser = argparse.ArgumentParser(description="URL redirector sho.com")

    parser.add_argument(
        "--port",
        "-p",
        action="store",
        type=int,
        default=8000,
        help="port to listen on (default 8000)",
    )
    parser.add_argument(
        "--ip",
        "-i",
        action="store",
        default="",
        help="host interface to listen on (default localhost)",
    )
    parser.add_argument(
        "--db",
        "-d",
        action="store",
        default="mappings.db",
        help="path to the sqlite3 database",
    )

    myargs = parser.parse_args()

    port = myargs.port
    host = myargs.ip
    db_path = myargs.db

    sho.urlmap.initialize_db(db_path)
    server_running = threading.Event()
    server_running.set()
    threading.Timer(10, thread_main, args=[server_running, db_path]).start()
    try:
        handler = http.server.ThreadingHTTPServer(
            (host, port), sho.request_handler.create_request_handler(db_path)
        )
        handler.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        handler.socket.close()
        server_running.clear()
