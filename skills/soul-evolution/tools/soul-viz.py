#!/usr/bin/env python3
"""
Soul Evolution Visualizer v5.7.1 (Modular Backend)
Backend server for the Project Genesis Singularity Dashboard.
Frontend assets are located in the ./web/ directory.
API logic is modularized in the ./api/ directory.
"""

import json
import sys
import os
import http.server
import socketserver
from api.data_utils import collect_data
from api.handlers_get import handle_get_request
from api.handlers_post import handle_post_request, handle_legacy_post

# --- HTML GENERATION ---

class DashboardTemplate:
    def __init__(self, template_path):
        self.template_path = template_path
        self.last_mtime = 0
        self.content = ""

    def render(self, data):
        data_json = json.dumps(data, indent=None, default=str)
        if not os.path.exists(self.template_path):
            return f"Template not found at {self.template_path}"
        
        # Hot-reload template if changed
        mtime = os.path.getmtime(self.template_path)
        if mtime > self.last_mtime:
            with open(self.template_path, "r") as f:
                self.content = f.read()
            self.last_mtime = mtime
            
        return self.content.replace("{data_json}", data_json)

# --- SERVER IMPLEMENTATION ---

def main():
    print("--- PROJECT GENESIS DASHBOARD v5.7.1 (MODULAR) STARTING ---", flush=True)
    workspace = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    port = 8080
    if "--serve" in sys.argv:
        idx = sys.argv.index("--serve")
        if idx + 1 < len(sys.argv) and sys.argv[idx + 1].isdigit():
            port = int(sys.argv[idx + 1])

    web_base = os.path.abspath(os.path.join(os.path.dirname(__file__), "web"))
    template_path = os.path.join(web_base, "index.html")
    dashboard_tpl = DashboardTemplate(template_path)

    class SoulEvolutionHandler(http.server.SimpleHTTPRequestHandler):
        def do_HEAD(self): self.do_GET()

        def do_GET(self):
            # 1. Static Web Assets
            if self.path.startswith("/web/"):
                rel = self.path[len("/web/"):]
                f_path = os.path.join(web_base, rel)
                if os.path.isfile(f_path):
                    self.serve_file(f_path)
                    return
            
            # 2. Reality Media (Images/Photos)
            if self.path.startswith("/media/"):
                rel = self.path[len("/media/"):]
                f_path = os.path.join(workspace, "memory", "reality", rel)
                if os.path.isfile(f_path):
                    self.serve_file(f_path)
                    return

            # 3. Application Pages
            if self.path == "/" or self.path == "/soul-evolution.html":
                data = collect_data(workspace)
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(dashboard_tpl.render(data).encode())
                return
            
            # 4. Modular API Endpoints
            if self.path.startswith("/api/"):
                handle_get_request(self, workspace)
                return

            self.send_error(404)

        def do_POST(self):
            # API POST
            if self.path.startswith("/api/"):
                handle_post_request(self, workspace)
                return
            
            # Legacy POST (SOUL.md, Reality Updates)
            handle_legacy_post(self, workspace)

        def serve_file(self, path):
            ext = os.path.splitext(path)[1].lower()
            ct = {
                ".html":"text/html", ".css":"text/css", ".js":"application/javascript",
                ".png":"image/png", ".jpg":"image/jpeg", ".jpeg":"image/jpeg", ".svg":"image/svg+xml"
            }.get(ext, "application/octet-stream")
            try:
                with open(path, "rb") as f: data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", ct)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except: self.send_error(404)

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), SoulEvolutionHandler) as httpd:
        print(f"Server active at http://localhost:{port}")
        httpd.serve_forever()

if __name__ == "__main__":
    main()
