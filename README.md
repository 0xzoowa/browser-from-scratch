# browser-from-scratch

a small browser built from scratch in python, as a way to understand how web browsers work under the hood.

the project is an ongoing exploration of the fundamentals of web communication, http, html parsing, and eventually how a browser turns web content into something a user can interact with.

rather than relying on browser libraries or frameworks, i'm implementing the basic mechanisms myself, experimenting with them, and documenting what i learn along the way.

## current implementation

the initial version is a minimal http client that:

- accepts a url through command-line arguments.
- extracts the url scheme, hostname, and path.
- establishes a tcp connection to a web server using python's `socket` module.
- constructs and sends an http `get` request.
- reads the http response, including its status line, headers, and body.
- performs basic html tag stripping to extract text from the response body.

## learning notes

this repository also serves as a learning journal. i'll document concepts, implementation decisions, experiments, and questions that come up as the project evolves.

topics explored so far:

- [ ] urls and their components
- [ ] tcp sockets and network connections
- [ ] http requests and responses
- [ ] http headers and response bodies
- [ ] html tags and basic text extraction
- [ ] client-server communication

## running the project

```bash
python3 browser.py http://example.org/
```

## project direction

the goal is to progressively understand and implement the mechanisms behind a browser, starting with the fundamentals and building upon each working piece.

this is a learning project, not a production-ready web browser.
