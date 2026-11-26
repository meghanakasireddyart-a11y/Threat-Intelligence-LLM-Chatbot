"""
Local HTTP Server for Lab 8 Replication & Failover Portal
Serves the web dashboard, scripts, screenshots, DOCX reports, and submission ZIP.
"""

import sys
import os
import webbrowser
import socket

# Compatibility for Python 2 and Python 3
if sys.version_info[0] >= 3:
    import http.server as server_module
    import socketserver
else:
    import SimpleHTTPServer as server_module
    import SocketServer as socketserver

PORT = 8008
WEB_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(WEB_DIR)


class Lab8RequestHandler(server_module.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Clean path
        clean_path = path.split('?', 1)[0].split('#', 1)[0]
        
        # Check if requesting root deliverables (docx, zip, screenshots)
        if clean_path.startswith('/Kasireddy') or clean_path.startswith('/NoSQL_') or clean_path.startswith('/screenshots') or clean_path.startswith('/Activity_'):
            full_path = os.path.join(ROOT_DIR, clean_path.lstrip('/'))
            if os.path.exists(full_path):
                return full_path

        # Otherwise serve from website directory
        return os.path.join(WEB_DIR, clean_path.lstrip('/'))

    def end_headers(self):
        # Prevent aggressive caching during lab exploration
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        server_module.SimpleHTTPRequestHandler.end_headers(self)


def find_available_port(start_port=8008):
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
    httpd = socketserver.TCPServer(server_address, Lab8RequestHandler)
    
    url = "http://localhost:{}/index.html".format(port)
    print("=" * 70)
    print("  NoSQL Lab 8: MongoDB Replication & Failover Web Portal")
    print("=" * 70)
    print("  Student : Kasireddy Meghana (24BTRCL119)")
    print("  Serving : {}".format(url))
    print("  Press Ctrl+C to terminate server.")
    print("=" * 70)

    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped gracefully.")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
