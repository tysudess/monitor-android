#!/usr/bin/env python3
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140 Safari/537.36"
channels = [
    ("g1", "https://www.youtube.com/channel/UCaGmdJSSiR7fkh2A-c6emsA/videos"),
    ("CNN Brasil", "https://www.youtube.com/@CNNBrasil/videos"),
    ("Jovem Pan News", "https://www.youtube.com/@jovempannews/videos"),
    ("GloboNews", "https://www.youtube.com/@globonews/videos"),
    ("Record News", "https://www.youtube.com/@recordnews/videos"),
    ("Jornal da Record", "https://www.youtube.com/@JornaldaRecord/videos"),
    ("Band Jornalismo", "https://www.youtube.com/@bandjornalismo/videos"),
    ("SBT News", "https://www.youtube.com/@sbtnews/videos"),
    ("Domingo Espetacular", "https://www.youtube.com/@domingoespetacular/videos"),
]
failed = []
for label, url in channels:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9"})
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read().decode("utf-8", "ignore")
            ok = r.status == 200 and "/videos" in r.geturl() and label.lower().replace(" ", "") in body.lower().replace(" ", "")
            print(f"{label}: status={r.status} final={r.geturl()} match={ok} bytes={len(body)}")
            if not ok:
                failed.append(label)
    except Exception as e:
        print(f"{label}: ERROR {type(e).__name__}: {e}")
        failed.append(label)
if failed:
    raise SystemExit("YouTube route verification failed: " + ", ".join(failed))
print(f"Verified {len(channels)} official YouTube /videos routes")
