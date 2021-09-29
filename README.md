# Url shortener

##  Program structure

This URL shortener consists of a small http server built with the `http.server` module of the python standard library. It can receive POST requests through a web page describing URL shortening requests. It can also receive GET request and will answer with HTTP 301 response redirecting the user to another website if possible. The existing shortened URLs and their target are stored in a `sqlite` database.

## How to run

You'll need python3. From the root directory, do `python -m sho` to run the server. Then, you can go to localhost on port 8000 (127.0.0.1:8000) to find the index page. From there you can send POST requests to the server containing the desired URL, SEO term and TTL. The server will then handle your request and redirect you to a page informing you that the shortened url has been created or explaining the reason why it wasn't.

* If you don't wish to give a SEO term or a TTL, just leave those fields empty
* The TTL is expressed in seconds, mainly for ease of testing

`python -m sho --help` will print the command line flags that you can use if you want to customize the application's behaviour.

## Tests

From the root folder, run `python -m unittest discover` to run the unittests.

## Code structure

Inside `sho` you will find the program logic:

* `server` contains the code initialising the database and the server
* `request_handler` contains the code receiving and sending http requests and responses
* `urlmap` contains the logic for creating new shortened urls
* `html_page_generator` contains rough html templates

Inside `test` you will find unittests.

