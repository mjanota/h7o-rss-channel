#!/usr/bin/env -S uv run
"""
Jednoduchý HTTP server pro testování RSS feedu.
Spustí lokální server, který zpřístupní h7o_feed.xml pro RSS čtečky.
"""

import http.server
import socketserver
import sys
from pathlib import Path


def run_server(port: int = 8000):
    """Spustí HTTP server na zadaném portu."""
    
    # Zajistí, že běžíme ve správném adresáři
    script_dir = Path(__file__).parent
    
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(script_dir), **kwargs)
        
        def end_headers(self):
            # Přidá správné CORS hlavičky pro přístup z různých domén
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            
            # Zajistí správný Content-Type pro XML soubory
            if self.path.endswith('.xml'):
                self.send_header('Content-Type', 'application/rss+xml; charset=utf-8')
            
            super().end_headers()
    
    try:
        with socketserver.TCPServer(("", port), CustomHandler) as httpd:
            print(f"✓ HTTP server běží na portu {port}")
            print(f"✓ RSS feed je dostupný na: http://localhost:{port}/h7o_feed.xml")
            print(f"✓ Pro zastavení serveru stiskněte Ctrl+C")
            print()
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Server zastaven")
        sys.exit(0)
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"✗ Chyba: Port {port} je již používán")
            print(f"  Zkuste jiný port: python server.py [PORT]")
            sys.exit(1)
        else:
            raise


if __name__ == "__main__":
    # Umožní zadat port jako argument
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)
