#!/usr/bin/env python3
"""Local preview server. Serves this directory on port 8765."""
import http.server
import os
import socketserver
from pathlib import Path

os.chdir(Path(__file__).resolve().parent)

PORT = 8765
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving on http://localhost:{PORT}")
    httpd.serve_forever()
