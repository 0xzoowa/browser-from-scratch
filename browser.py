import socket
import sys
import ssl
import time
import gzip

sockets = {}
cache = {}

class URL:
    def __init__(self, url):
        self.view_source = False

        if url.startswith("view-source:"):
            self.view_source = True
            url = url[len("view-source:"):]

        self.scheme, url = url.split(":",1)
       
        if self.scheme == "http":
            self.port = 80
            url = url.removeprefix("//")

        elif self.scheme == "https":
            self.port = 443
            url = url.removeprefix("//")

        elif self.scheme == "file":
            self.path = url.removeprefix("//")
            return

        elif self.scheme == "data":
            self.data = url
            return

        else:
            raise ValueError("Unsupported scheme: " + self.scheme)

        if "/" not in url:
            url = url + "/"
            
        self.host, url = url.split("/",1)
        self.path = "/" + url

        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

    def request(self, version="1.1",  redirect_count=0):
        
        if self.scheme == "file":
            with open(self.path, "r", encoding="utf8") as f:
                return f.read()
        elif self.scheme == "data":
            metadata, content = self.data.split(",", 1)
            return content
        
        elif self.scheme == "http" or self.scheme == "https" :

            socket_key = (self.host, self.port)
            cache_key = (self.scheme, self.host, self.port, self.path)

            if cache_key in cache:
                expires, body = cache[cache_key]

                if time.monotonic() < expires:
                    print("CACHE HIT")
                    return body
                else:
                    del cache[cache_key]

            if socket_key in sockets:
                 s = sockets[socket_key]
            else:
         
                s = socket.socket(
                    family=socket.AF_INET,
                    type=socket.SOCK_STREAM,
                    proto=socket.IPPROTO_TCP
                )

                s.connect(socket_key)
                sockets[socket_key] = s

            if self.scheme == "https":
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=self.host)
            
            request = "GET {} HTTP/{}\r\n".format(self.path, version)

            request_headers = {
                    "Host": self.host,
                    "Connection": "close", #"keep-alive",
                    "User-Agent": " IamGroot/0.1",
                    "Accept-Encoding": "gzip"
            }

            for k,v in request_headers.items():
                request += "{}: {}\r\n".format(k,v)
            
            request += "\r\n"
            s.sendall(request.encode("utf8")) #converts text to binary
            response = s.makefile("rb")
            statusline = response.readline().decode("utf8")
            request_version, status, explanation = statusline.split(" ", 2)

            response_headers = {}
            while True:
                line = response.readline().decode("utf8")
                if(line == "\r\n") : break
                header, value = line.split(":", 1)
                response_headers[header.casefold()] = value.strip()
            

            with response:
                cl = response_headers.get("content-length")
                if cl and cl.isdigit():
                    content = response.read(int(cl)) 
                else:
                    print("ENTERING ELSE BLOCK - WAITING ON READ()...")
                    content = response.read() #response.read() does not return until the socket closes

                if response_headers.get("content-encoding") == "gzip":
                    content = gzip.decompress(content)

            body = content.decode("utf8")
            status_code = int(status)

            if status_code in range(300, 400) and "location" in response_headers:

                if redirect_count >= 10:
                    raise Exception("Too many redirects")

                location = response_headers["location"]

                if location.startswith("/"):
                    location = "{}://{}:{}{}".format(
                        self.scheme,
                        self.host,
                        self.port,
                        location
                    )

                new_url = URL(location)
                new_url.view_source = self.view_source

                return new_url.request(version, redirect_count + 1)   
 
            if status == "200":
                cache_control = response_headers.get("cache-control") #.get() safely returns None instead of crashing 
                max_age = get_cache_lifetime(cache_control)

                if max_age is not None and max_age > 0:
                    expires = time.monotonic() + max_age
                    cache[cache_key] = (expires, body)
                    
            return body

def get_cache_lifetime(cache_control):

    if not cache_control: 
        return None

    directives = [
        directive.strip().lower()
        for directive in cache_control.split(",")

    ]
    if "no-store" in directives:
        return None

    if len(directives) != 1:
        return None

    directive = directives[0] #priority is given to the first directive

    if not directive.startswith("max-age="):
        return None

    try:
        return int(directive.split("=", 1)[1])
    except ValueError:
        return None

def show(body, view_source):

    if view_source:
        print(body, end="")
        return
    
    in_tag = False
    output = ""
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            output += c

    output = output.replace("&lt;", "<")
    output = output.replace("&gt;", ">")

    print(output, end="")


def load(url):
    body = url.request()
    show(body, url.view_source)
  

if __name__ == "__main__":
    load(URL(sys.argv[1]))

    
