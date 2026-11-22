#!/usr/bin/env python3
"""Regenerate the base64-embedded nginx theme config inside
xbtc-datum/docker-compose.yml from theme/assets/crypto-eire.css.

Why base64-in-compose instead of a mounted file: umbrelOS does not copy non-data
app subdirs into app-data, so a bind mount of theme/nginx.conf comes up as an empty
directory and nginx has no config. Embedding the whole config (incl. the minified
theme CSS) in the compose `command` ships it with the app and survives updates.

Usage:  python3 xbtc-datum/theme/build.py
"""
import re, base64, pathlib

HERE = pathlib.Path(__file__).resolve().parent          # .../xbtc-datum/theme
APP = HERE.parent                                        # .../xbtc-datum

css = (HERE / "assets" / "crypto-eire.css").read_text()
css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)          # strip comments
css = re.sub(r"\s+", " ", css).strip()                   # collapse whitespace
css = re.sub(r"\s*([{}:;,])\s*", r"\1", css)             # tighten around punctuation

CONF = r'''server {
    listen 80;
    server_name _;
    location / {
        proxy_pass http://xbtc-datum_datum_1:21009;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header Accept-Encoding "";
        proxy_redirect off;
        sub_filter_once off;
        sub_filter_types text/html;
        sub_filter '</head>' '<style>__CSS__</style></head>';
        sub_filter '/assets/icons/datum_logo.svg' 'https://crypto-eire.com/crypto-eire-icon.png';
        sub_filter 'DATUM <span>GATEWAY</span>' 'Crypto-Éire <span>xBTC</span>';
        sub_filter 'DATUM Gateway Status' 'Crypto-Éire xBTC — DATUM';
    }
}
'''.replace("__CSS__", css)

b64 = base64.b64encode(CONF.encode()).decode()
cmd = "echo %s | base64 -d > /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'" % b64

compose = APP / "docker-compose.yml"
text = compose.read_text()
new = re.sub(
    r'- "echo [^"]*base64 -d > /etc/nginx/conf\.d/default\.conf && exec nginx -g \'daemon off;\'"',
    '- "' + cmd + '"',
    text,
)
if new == text:
    print("no change (compose already matches crypto-eire.css); b64 len", len(b64))
else:
    compose.write_text(new)
    print("docker-compose.yml theme config regenerated; b64 len", len(b64))
