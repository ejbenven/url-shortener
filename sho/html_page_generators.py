"""
This contains several templates for html pages that the application needs
"""

_HEADER = """<html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">

            <title>sho.com</title>
            <meta name="description" content="{}">
            <meta name="author" content="Eloi Benvenuti">

        </head>"""


def name_collision_page(name):
    output = (
        _HEADER.format("Name unavailable")
        + """
        <body>
            <h2>Sorry, the short URL name {} is already taken.</h2>
        </body>
    </html>""".format(
            name
        )
    )
    return output


def new_mapping_page(short_url, original_url):
    output = (
        _HEADER.format("Short URL created")
        + """
        <body>
            <h2>{} now points to {}</h2>
        </body>
    </html>""".format(
            short_url, original_url
        )
    )
    return output


def incorrect_submission_page():
    output = (
        _HEADER.format("Incorrect submission")
        + """
        <body>
            <h2>URL field must be non-empty</h2>
        </body>
    </html>"""
    )
    return output
