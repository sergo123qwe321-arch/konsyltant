#!/bin/sh
set -e

mkdir -p /etc/letsencrypt/live/xn--g1a2b.site
mkdir -p /var/www/certbot

if [ ! -f /etc/letsencrypt/live/xn--g1a2b.site/fullchain.pem ] || [ ! -f /etc/letsencrypt/live/xn--g1a2b.site/privkey.pem ]; then
    echo "[SSL INIT] SSL certificate not found. Generating fallback self-signed certificate for xn--g1a2b.site..."
    if ! command -v openssl >/dev/null 2>&1; then
        apk update >/dev/null 2>&1 && apk add --no-cache openssl >/dev/null 2>&1
    fi
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/letsencrypt/live/xn--g1a2b.site/privkey.pem \
        -out /etc/letsencrypt/live/xn--g1a2b.site/fullchain.pem \
        -subj "/CN=xn--g1a2b.site" >/dev/null 2>&1
    echo "[SSL INIT] Fallback certificate ready."
else
    echo "[SSL INIT] Certificate already exists."
fi
