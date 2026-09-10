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

def verify(label: str, handle: str):
    url = f"https://www.youtube.com/{handle}/videos"
    try:
        body = fetch(url)
        normalized = body.lower().replace(" ", "")
        ok = (label.lower().replace(" ", "") in normalized) or (handle.lower() in body.lower())
        print(f"VERIFY {label}: handle={handle} videos_tab={url} body_match={ok} bytes={len(body)}")
    except Exception as e:
        print(f"VERIFY {label}: ERROR {type(e).__name__}: {e}")

def discover(tag: str, query_text: str, needle: str):
    query = urllib.parse.quote_plus(query_text)
    try:
        body = fetch(f"https://www.youtube.com/results?search_query={query}")
        pairs = []
        for m in re.finditer(r'"channelRenderer":\{(.{0,6000}?)\}\}', body):
            block = m.group(1)
            title_m = re.search(r'"title":\{"simpleText":"([^"]+)"', block)
            id_m = re.search(r'"channelId":"([^"]+)"', block)
            url_m = re.search(r'"canonicalBaseUrl":"(/[^"]+)"', block)
            if title_m and id_m:
                pairs.append((html.unescape(title_m.group(1)), id_m.group(1), url_m.group(1) if url_m else ""))
        print(f"DISCOVER_{tag}_CHANNELS=" + json.dumps(pairs[:15], ensure_ascii=False))
        idx = body.lower().find(needle.lower())
        if idx >= 0:
            chunk = body[max(0, idx-15000):idx+15000]
            handles = sorted(set(re.findall(r'\\?"canonicalBaseUrl\\?":\\?"(/@[^\\"]+)', chunk)))
            print(f"DISCOVER_{tag}_HANDLES_NEAR_MATCH=" + json.dumps(handles, ensure_ascii=False))
    except Exception as e:
        print(f"DISCOVER {tag}: ERROR {type(e).__name__}: {e}")

channels = [
    ("CNN Brasil", "@CNNBrasil"),
    ("Jovem Pan News", "@jovempannews"),
    ("GloboNews", "@globonews"),
    ("Record News", "@recordnews"),
    ("Jornal da Record", "@JornaldaRecord"),
    ("Band Jornalismo", "@bandjornalismo"),
    ("SBT News", "@sbtnews"),
    ("Domingo Espetacular", "@domingoespetacular"),
]
for label, handle in channels:
    verify(label, handle)

discover("G1", "g1 Globo notícias canal oficial", "g1")
discover("DOMINGO", "Domingo Espetacular Record TV", "Domingo Espetacular")
