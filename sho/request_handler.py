"""
Contains the request handler factory

The request handler is responsible for querying the database, issuing redirects and creating
new urls.
"""

import cgi
import http
import http.server

import sho.urlmap


def create_request_handler(db_path):
    class ServerRequestHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/index.html":
                with open("index.html", "rb") as f:
                    self.send_response(http.HTTPStatus.OK)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(f.read())
            else:
                path = sho.urlmap.get_long_url(self.path, db_path)

                if not path:
                    self.send_response(http.HTTPStatus.NOT_FOUND)
                    self.end_headers()
                else:
                    self.send_response(http.HTTPStatus.MOVED_PERMANENTLY)
                    self.send_header("Location", path)
                    self.end_headers()

        def do_POST(self):
            ctype, pdict = cgi.parse_header(self.headers.get("Content-Type"))
            pdict["boundary"] = bytes(pdict["boundary"], "utf-8")

            if ctype == "multipart/form-data":
                self.send_response(http.HTTPStatus.SEE_OTHER)
                self.send_header("Content-Type", "text/html")
                self.end_headers()

                fields = cgi.parse_multipart(self.rfile, pdict)

                output = sho.urlmap.handle_request(fields, db_path)
                self.wfile.write(output.encode())
            else:
                self.send_response(http.HTTPStatus.SEE_OTHER)
                self.end_headers()

    return ServerRequestHandler
