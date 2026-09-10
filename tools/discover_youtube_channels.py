#!/usr/bin/env python3
import html
import json
import re
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140 Safari/537.36"

def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.7"})
    with urllib.request.urlopen(req, timeout=20) as r:
        print(f"FETCH {url} -> {r.status} {r.geturl()}")
        return r.read().decode("utf-8", "ignore")

# Verify the currently configured channel /videos routes.
channels = [
    ("g1", "@g1"),
    ("CNN Brasil", "@CNNBrasil"),
    ("Jovem Pan News", "@jovempannews"),
    ("GloboNews", "@globonews"),
    ("Record News", "@recordnews"),
    ("Jornal da Record", "@JornaldaRecord"),
    ("Band Jornalismo", "@bandjornalismo"),
    ("SBT News", "@sbtnews"),
]
for label, handle in channels:
    url = f"https://www.youtube.com/{handle}/videos"
    try:
        body = fetch(url)
        ok = (label.lower().replace(" ", "") in body.lower().replace(" ", "")) or (handle.lower() in body.lower())
        print(f"VERIFY {label}: handle={handle} videos_tab={url} body_match={ok} bytes={len(body)}")
    except Exception as e:
        print(f"VERIFY {label}: ERROR {type(e).__name__}: {e}")

# Discover the official/most relevant YouTube channel used for Domingo Espetacular.
query = urllib.parse.quote_plus("Domingo Espetacular Record TV")
try:
    body = fetch(f"https://www.youtube.com/results?search_query={query}")
    pairs = []
    # ytInitialData contains channelRenderer blocks with channelId/title/navigationEndpoint.
    for m in re.finditer(r'"channelRenderer":\{(.{0,6000}?)\}\}', body):
        block = m.group(1)
        title_m = re.search(r'"title":\{"simpleText":"([^"]+)"', block)
        id_m = re.search(r'"channelId":"([^"]+)"', block)
        url_m = re.search(r'"canonicalBaseUrl":"(/[^"]+)"', block)
        if title_m and id_m:
            pairs.append((html.unescape(title_m.group(1)), id_m.group(1), url_m.group(1) if url_m else ""))
    print("DISCOVER_DOMINGO_CHANNELS=" + json.dumps(pairs[:12], ensure_ascii=False))
    # Also print handles mentioned around Domingo Espetacular in the raw HTML.
    idx = body.lower().find("domingo espetacular")
    if idx >= 0:
        chunk = body[max(0, idx-12000):idx+12000]
        handles = sorted(set(re.findall(r'\\?"canonicalBaseUrl\\?":\\?"(/@[^\\"]+)', chunk)))
        print("DISCOVER_DOMINGO_HANDLES_NEAR_MATCH=" + json.dumps(handles, ensure_ascii=False))
except Exception as e:
    print(f"DISCOVER Domingo Espetacular: ERROR {type(e).__name__}: {e}")
