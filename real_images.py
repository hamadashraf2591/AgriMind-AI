import os, io, sys, json, time, urllib.request, urllib.parse
from PIL import Image, ImageOps

OUT = os.path.join("static", "img")
os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "AgriMindAI/2.0 (student project; educational use)"}
LANCZOS = getattr(Image, "Resampling", Image).LANCZOS
BAD = ("map", "diagram", "logo", "icon", "chart", "graph", "drawing", "flag", "coat of arms", "locator",
       "poster", "stamp", "illustration", "plan", "scheme", "cartoon", "screenshot", "text", "label")

# name : (width, height, [search queries])
JOBS = {
    "hero.jpg":       (1920, 1080, ["green wheat field sunset", "wheat field landscape", "agricultural field landscape"]),
    "bg.jpg":         (1920, 1080, ["rice terraces", "green farmland landscape", "agriculture landscape fields"]),
    "leaf.jpg":       (900, 700,   ["green leaf macro", "fresh green leaf", "leaf close-up"]),
    "disease.jpg":    (800, 600,   ["plant disease leaf", "leaf blight", "leaf fungal disease"]),
    "weather.jpg":    (1600, 600,  ["clouds over field", "cumulus clouds farmland", "sky clouds countryside"]),
    "irrigation.jpg": (800, 600,   ["irrigation sprinkler field", "center pivot irrigation", "drip irrigation"]),
    "yield.jpg":      (800, 600,   ["wheat harvest", "combine harvester wheat", "grain harvest"]),
    "fertilizer.jpg": (1600, 600,  ["plowed field soil", "tilled farmland", "fertilizer spreading field"]),
    "advisor.jpg":    (1600, 600,  ["crop rows farmland", "vegetable field rows", "farm fields aerial"]),
    "history.jpg":    (1600, 600,  ["farmer in field", "farmer working field", "Pakistani farmer"]),
    "library.jpg":    (1600, 600,  ["green leaves foliage", "plant leaves", "leaves texture"]),
    "models.jpg":     (1600, 600,  ["tractor in field", "modern tractor farm", "tractor plowing"]),
    "healthy.jpg":    (800, 500,   ["healthy green leaf", "fresh green leaves", "green plant leaf"]),
    "blight.jpg":     (800, 500,   ["late blight potato leaf", "leaf blight", "northern corn leaf blight"]),
    "rust.jpg":       (800, 500,   ["wheat leaf rust", "wheat stem rust", "rust fungus leaf"]),
    "mildew.jpg":     (800, 500,   ["powdery mildew leaf", "powdery mildew", "mildew on leaves"]),
    "spot.jpg":       (800, 500,   ["leaf spot disease", "cercospora leaf spot", "septoria leaf spot"]),
    "wheat.jpg":      (400, 400,   ["wheat ears", "wheat close up", "wheat field"]),
    "rice.jpg":       (400, 400,   ["rice paddy field", "rice plants", "paddy field"]),
    "maize.jpg":      (400, 400,   ["maize field", "corn plant cob", "maize plant"]),
    "cotton.jpg":     (400, 400,   ["cotton boll", "cotton plant field", "cotton plant"]),
    "sugarcane.jpg":  (400, 400,   ["sugarcane field", "sugarcane plants", "sugar cane"]),
}

def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))

def good_title(t):
    t = (t or "").lower()
    return not any(b in t for b in BAD)

def ratio_ok(iw, ih, w, h):
    if not iw or not ih:
        return True
    target = w / h
    if target > 1.2:
        return iw / ih > 1.15
    return True

def commons(q, w, h):
    params = {"action": "query", "format": "json", "generator": "search",
              "gsrsearch": f"filetype:bitmap {q}", "gsrnamespace": 6, "gsrlimit": 25,
              "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": w}
    data = get_json("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params))
    pages = sorted(data.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0))
    out = []
    for p in pages:
        ii = (p.get("imageinfo") or [{}])[0]
        if ii.get("mime") != "image/jpeg" or not good_title(p.get("title")):
            continue
        if ii.get("width", 0) < w * 0.6 or not ratio_ok(ii.get("width"), ii.get("height"), w, h):
            continue
        url = ii.get("thumburl") or ii.get("url")
        out.append({"url": url, "title": p.get("title", ""), "source": "Wikimedia Commons",
                    "page": ii.get("descriptionurl", "")})
    return out

def openverse(q, w, h):
    params = {"q": q, "page_size": 20, "mature": "false", "extension": "jpg"}
    data = get_json("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(params))
    out = []
    for r in data.get("results", []):
        if (r.get("width") or 0) < w * 0.6 or not good_title(r.get("title")):
            continue
        if not ratio_ok(r.get("width"), r.get("height"), w, h):
            continue
        out.append({"url": r.get("url"), "title": r.get("title", ""), "source": "Openverse",
                    "page": r.get("foreign_landing_url", ""), "license": r.get("license", "")})
    return out

def download(url, w, h, path):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        data = r.read()
    im = Image.open(io.BytesIO(data)).convert("RGB")
    if im.width < 250 or im.height < 200:
        raise ValueError("too small")
    ImageOps.fit(im, (w, h), LANCZOS).save(path, "JPEG", quality=88, optimize=True)

# ---------------- arguments ----------------
args = sys.argv[1:]
pick = 1
if "--pick" in args:
    i = args.index("--pick")
    pick = max(1, int(args[i + 1]))
    del args[i:i + 2]
only = [a for a in args if a.endswith(".jpg")]
targets = {k: v for k, v in JOBS.items() if not only or k in only}

credits_path = os.path.join(OUT, "credits.json")
credits = json.load(open(credits_path, encoding="utf-8")) if os.path.exists(credits_path) else {}

print("=" * 60)
print("   AgriMind AI - Downloading REAL photos")
print("=" * 60)
ok = fail = 0
for name, (w, h, queries) in targets.items():
    path = os.path.join(OUT, name)
    cands, seen = [], set()
    for q in queries:
        for finder in (commons, openverse):
            try:
                for c in finder(q, w, h):
                    if c["url"] and c["url"] not in seen:
                        seen.add(c["url"]); cands.append(c)
            except Exception:
                pass
        if len(cands) >= pick + 4:
            break
    done = False
    for c in cands[pick - 1:]:
        try:
            download(c["url"], w, h, path)
            credits[name] = c
            title = c["title"].replace("File:", "")[:45]
            print(f"  [REAL] {name:<15} <- {title}")
            ok += 1; done = True
            break
        except Exception:
            continue
    if not done:
        print(f"  [KEEP] {name:<15} (no photo found, old image kept)")
        fail += 1
    time.sleep(0.4)

json.dump(credits, open(credits_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("=" * 60)
print(f"   Real photos: {ok}   |   Kept old: {fail}")
print("   Photo credits saved in static/img/credits.json")
print("=" * 60)
