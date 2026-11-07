import http.server
import socketserver
import json
import sqlite3
import os

PORT = 8000
DB_PATH = os.path.join(os.path.dirname(__file__), "offers.sqlite3")

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if self.path.startswith('/api/offers'):
            self.get_offers()
        elif self.path.startswith('/api/stats'):
            self.get_stats()
        else:
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

    def get_offers(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute("SELECT * FROM offers WHERE status IN ('pending', 'accepted') ORDER BY created DESC").fetchall()
            data = [dict(r) for r in rows]
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        finally:
            conn.close()

    def get_stats(self):
        conn = sqlite3.connect(DB_PATH)
        try:
            total = conn.execute("SELECT COUNT(*) FROM offers").fetchone()[0]
            pending = conn.execute("SELECT COUNT(*) FROM offers WHERE status = 'pending'").fetchone()[0]
            accepted = conn.execute("SELECT COUNT(*) FROM offers WHERE status = 'accepted'").fetchone()[0]
            data = {"total": total, "pending": pending, "accepted": accepted}
            self.wfile.write(json.dumps(data).encode('utf-8'))
        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        finally:
            conn.close()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
