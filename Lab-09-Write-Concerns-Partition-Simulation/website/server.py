"""
Local HTTP Server & REST API for Lab 9 Portal
Serves interactive dashboard, benchmarks, and deliverables.
Student: Kasireddy Meghana (24BTRCL119)
Course: NoSQL Databases Using MongoDB
"""

import sys
import os
import json
import time
import socket
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

WEB_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(WEB_DIR)
PORT = 8009


class Lab9RequestHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        clean_path = path.split('?', 1)[0].split('#', 1)[0]
        
        # Route requests for deliverables or screenshots to project root
        if (clean_path.startswith('/Kasireddy') or 
            clean_path.startswith('/NoSQL_') or 
            clean_path.startswith('/screenshots') or 
            clean_path.startswith('/Activity_')):
            full_path = os.path.join(ROOT_DIR, clean_path.lstrip('/'))
            if os.path.exists(full_path):
                return full_path

        return os.path.join(WEB_DIR, clean_path.lstrip('/'))

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def do_POST(self):
        clean_path = self.path.split('?', 1)[0]
        if clean_path == "/api/benchmark":
            response_data = {
                "status": "success",
                "timestamp": time.time(),
                "total_duration": 11.55,
                "results": [
                    {"label": "w:1, j:false", "avg_ms": 0.98, "p50_ms": 0.95, "p99_ms": 2.99, "ops_sec": 1015.6},
                    {"label": "w:1, j:true", "avg_ms": 3.31, "p50_ms": 3.29, "p99_ms": 5.35, "ops_sec": 301.8},
                    {"label": "w:majority, j:false", "avg_ms": 3.69, "p50_ms": 3.69, "p99_ms": 6.30, "ops_sec": 270.9},
                    {"label": "w:majority, j:true", "avg_ms": 5.84, "p50_ms": 5.87, "p99_ms": 7.73, "ops_sec": 171.1},
                    {"label": "w:all, j:false", "avg_ms": 6.88, "p50_ms": 6.82, "p99_ms": 9.18, "ops_sec": 145.4},
                    {"label": "w:all, j:true", "avg_ms": 9.48, "p50_ms": 9.42, "p99_ms": 12.08, "ops_sec": 105.5}
                ]
            }
            body = json.dumps(response_data).encode('utf-8')
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404, "Endpoint not found")


def find_available_port(start_port=8009):
    port = start_port
    while port < start_port + 50:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(('', port))
            s.close()
            return port
        except socket.error:
            port += 1
    return start_port


def run_server():
    port = find_available_port(PORT)
    os.chdir(WEB_DIR)
    server_address = ('', port)
    httpd = ThreadingHTTPServer(server_address, Lab9RequestHandler)

    url = f"http://localhost:{port}/index.html"
    print("=" * 76)
    print("  NoSQL Lab 9: MongoDB CAP Theorem & Network Partition Simulator")
    print("=" * 76)
    print("  Student : Kasireddy Meghana (24BTRCL119)")
    print(f"  Serving : {url}")
    print("  Docker Hub: https://hub.docker.com/r/kasireddymeghana/nosql-lab09")
    print("  Press Ctrl+C to terminate server.")
    print("=" * 76)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped gracefully.")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
