import os, io, sys, math, random, urllib.request
from PIL import Image, ImageDraw, ImageFilter, ImageChops

OUT = os.path.join("static", "img")
os.makedirs(OUT, exist_ok=True)
OFFLINE = "--offline" in sys.argv
FORCE = "--force" in sys.argv

# ======================= DRAWING HELPERS =======================
def vgrad(w, h, top, bot):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    return img

def sun(d, x, y, r, col):
    for k in range(10, 0, -1):
        rr = r * (1 + k * 0.4)
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col + (10,))
    d.ellipse([x - r, y - r, x + r, y + r], fill=col + (255,))

def clouds(d, w, h, rnd, n):
    for _ in range(n):
        cx, cy, s = rnd.uniform(0, w), rnd.uniform(h * .06, h * .32), rnd.uniform(.05, .1) * w
        for _ in range(7):
            ox, oy, r = rnd.uniform(-s, s), rnd.uniform(-s * .2, s * .2), rnd.uniform(.35, .6) * s
            d.ellipse([cx + ox - r, cy + oy - r * .55, cx + ox + r, cy + oy + r * .55], fill=(255, 255, 255, 120))

def hills(d, w, h, rnd, cols, start=.55, step=.08):
    base = h * start
    for i, c in enumerate(cols):
        base = h * (start + step * i)
        amp, f, ph = h * rnd.uniform(.015, .045), rnd.uniform(1, 2.5), rnd.uniform(0, 6.28)
        pts = [(x, base + amp * math.sin(x / w * f * 6.28 + ph)) for x in range(0, w + 21, 20)]
        d.polygon(pts + [(w, h), (0, h)], fill=c)
    return base

def rows(d, w, h, y0, col, n=26):
    vx = w / 2
    for i in range(-n, n + 1):
        xb = vx + i * w / n * 1.3
        d.line([(vx + (xb - vx) * .1, y0), (xb, h)], fill=col, width=max(2, w // 320))

def landscape(w, h, seed, sky, cols, sun_col=(255, 220, 130), row_col=(0, 0, 0, 55), n_clouds=5, sx=.72, sy=.3):
    rnd = random.Random(seed)
    img = vgrad(w, h, *sky)
    d = ImageDraw.Draw(img, "RGBA")
    if sun_col:
        sun(d, w * sx, h * sy, min(w, h) * .06, sun_col)
    clouds(d, w, h, rnd, n_clouds)
    base = hills(d, w, h, rnd, cols)
    if row_col:
        rows(d, w, h, base + h * .07, row_col)
    return img.filter(ImageFilter.GaussianBlur(1))

# ======================= LEAVES =======================
LEAF = {
    "healthy": dict(col=(64, 165, 74), n=0),
    "blight":  dict(col=(125, 150, 62), n=10, spot=(110, 68, 30), sz=(.08, .18), a=235),
    "rust":    dict(col=(84, 150, 62), n=110, spot=(210, 115, 35), sz=(.008, .02), a=255),
    "mildew":  dict(col=(92, 150, 84), n=40, spot=(238, 242, 236), sz=(.03, .08), a=150),
    "spot":    dict(col=(70, 152, 66), n=28, spot=(92, 52, 26), sz=(.018, .035), a=255, halo=(225, 205, 70)),
}

def half_width(W, t):
    return W * math.sin(math.pi * t) ** .9 * (1 - .3 * t)

def draw_leaf(img, cx, cy, L, ang, kind, rnd):
    cfg, W, n = LEAF[kind], L * .42, 70
    top = [(-L + 2 * L * i / n, -half_width(W, i / n)) for i in range(n + 1)]
    bot = [(x, -y) for x, y in top]
    ca, sa = math.cos(ang), math.sin(ang)
    tr = lambda x, y: (cx + x * ca - y * sa, cy + x * sa + y * ca)
    pts = [tr(x, y) for x, y in top + bot[::-1]]

    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(x + L * .05, y + L * .07) for x, y in pts], fill=(0, 0, 0, 130))
    sh = sh.filter(ImageFilter.GaussianBlur(L * .06))
    img.paste(sh, (0, 0), sh)

    d = ImageDraw.Draw(img, "RGBA")
    d.polygon(pts, fill=cfg["col"])
    light = tuple(min(255, c + 45) for c in cfg["col"])
    d.polygon(pts[:n + 1], fill=light + (70,))
    vc = tuple(min(255, c + 75) for c in cfg["col"]) + (210,)
    d.line([tr(-L * 1.18, 0), tr(L, 0)], fill=vc, width=max(2, int(L * .02)))
    for i in range(1, 9):
        t = i / 9
        x, yy = -L + 2 * L * t, half_width(W, t) * .85
        for s in (-1, 1):
            d.line([tr(x, 0), tr(x + L * .22, s * yy)], fill=vc, width=max(1, int(L * .01)))

    if cfg["n"]:
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        for _ in range(cfg["n"]):
            t = rnd.uniform(.55, .97) if kind == "blight" else rnd.uniform(.08, .92)
            x = -L + 2 * L * t
            my = half_width(W, t) * .85
            px, py = tr(x, rnd.uniform(-my, my))
            r = L * rnd.uniform(*cfg["sz"])
            if cfg.get("halo"):
                ld.ellipse([px - r * 1.9, py - r * 1.9, px + r * 1.9, py + r * 1.9], fill=cfg["halo"] + (170,))
            ld.ellipse([px - r, py - r, px + r, py + r], fill=cfg["spot"] + (cfg["a"],))
        if kind in ("blight", "mildew"):
            layer = layer.filter(ImageFilter.GaussianBlur(L * .015))
        mask = Image.new("L", img.size, 0)
        ImageDraw.Draw(mask).polygon(pts, fill=255)
        layer.putalpha(ImageChops.multiply(layer.getchannel("A"), mask))
        img.paste(layer, (0, 0), layer)

def leaf_image(w, h, kind, seed, count=1):
    rnd = random.Random(seed)
    img = vgrad(w, h, (26, 72, 42), (6, 26, 15))
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(28):
        x, y, r = rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(.02, .08) * min(w, h)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(130, 210, 130, rnd.randint(10, 35)))
    L = min(w * .42, h * .55)
    if count == 1:
        draw_leaf(img, w / 2, h / 2, L, -0.35, kind, rnd)
    else:
        for (fx, fy, s, a, k) in [(.2, .55, .5, -.5, "spot"), (.5, .45, .6, .25, "healthy"), (.8, .55, .5, -.3, "rust")]:
            draw_leaf(img, w * fx, h * fy, L * s, a, k, rnd)
    return img

# ======================= CROPS =======================
SKY = ((110, 170, 225), (215, 235, 245))

def crop_image(kind, w=400, h=400):
    rnd = random.Random(kind)
    if kind == "wheat":
        img = landscape(w, h, 3, ((120, 175, 230), (250, 215, 150)), [(222, 180, 80), (205, 160, 60)], row_col=None, n_clouds=2)
        d = ImageDraw.Draw(img, "RGBA")
        for _ in range(int(w / 7)):
            x, top, lean = rnd.uniform(0, w), rnd.uniform(h * .45, h * .78), rnd.uniform(-15, 15)
            d.line([(x, h), (x + lean, top)], fill=(185, 140, 50), width=2)
            for k in range(7):
                gy = top + k * 7
                d.ellipse([x + lean - 4, gy - 6, x + lean + 4, gy + 6], fill=(238, 195, 95))
    elif kind == "rice":
        img = landscape(w, h, 4, SKY, [(96, 175, 80), (78, 160, 70)], row_col=None, n_clouds=3)
        d = ImageDraw.Draw(img, "RGBA")
        d.rectangle([0, h * .68, w, h], fill=(90, 150, 170))
        for _ in range(40):
            x, y = rnd.uniform(0, w), rnd.uniform(h * .7, h)
            d.line([(x, y), (x + rnd.uniform(15, 40), y)], fill=(200, 230, 240, 120), width=2)
        for _ in range(int(w / 6)):
            x, y = rnd.uniform(0, w), rnd.uniform(h * .7, h)
            for a in range(-3, 4):
                d.line([(x, y), (x + a * 5, y - rnd.uniform(25, 45))], fill=(70, 160, 60), width=2)
    elif kind == "maize":
        img = landscape(w, h, 5, SKY, [(70, 140, 60), (50, 120, 45)], row_col=None)
        d = ImageDraw.Draw(img, "RGBA")
        for _ in range(int(w / 15)):
            x, top = rnd.uniform(0, w), rnd.uniform(h * .2, h * .45)
            d.line([(x, h), (x, top)], fill=(60, 125, 45), width=5)
            for k in range(5):
                y, s = top + (h - top) * (k + 1) / 7, (-1) ** k
                d.line([(x, y), (x + s * 45, y - 25), (x + s * 70, y + 5)], fill=(80, 160, 60), width=4, joint="curve")
            d.line([(x, top), (x, top - 20)], fill=(225, 205, 110), width=3)
            d.ellipse([x + 3, top + 60, x + 16, top + 95], fill=(240, 205, 85))
    elif kind == "cotton":
        img = landscape(w, h, 6, SKY, [(80, 140, 60), (60, 120, 50)], row_col=None)
        d = ImageDraw.Draw(img, "RGBA")
        for _ in range(45):
            x, y, r = rnd.uniform(0, w), rnd.uniform(h * .5, h), rnd.uniform(18, 35)
            d.ellipse([x - r, y - r * .7, x + r, y + r * .7], fill=(45, 105, 40))
        for _ in range(int(w / 5)):
            x, y, r = rnd.uniform(0, w), rnd.uniform(h * .45, h), rnd.uniform(5, 10)
            d.ellipse([x - r + 2, y - r + 2, x + r + 2, y + r + 2], fill=(150, 150, 150, 120))
            d.ellipse([x - r, y - r, x + r, y + r], fill=(250, 250, 248))
    else:  # sugarcane
        img = landscape(w, h, 7, SKY, [(90, 150, 60), (70, 130, 50)], row_col=None)
        d = ImageDraw.Draw(img, "RGBA")
        for _ in range(int(w / 18)):
            x, top, cw = rnd.uniform(0, w), rnd.uniform(h * .1, h * .35), rnd.uniform(7, 12)
            d.rectangle([x, top, x + cw, h], fill=(135, 175, 75))
            for y in range(int(top), h, 28):
                d.line([(x, y), (x + cw, y)], fill=(90, 120, 50), width=3)
            for s in (-1, 1):
                d.line([(x + cw / 2, top), (x + s * 60, top + 50)], fill=(70, 150, 55), width=4)
    return img

# ======================= IMAGE LIST =======================
L1 = [(120, 150, 60), (90, 130, 50), (62, 112, 42), (46, 92, 34)]
JOBS = [
    ("hero.jpg", 1920, 1080, "farm,field", lambda w, h: landscape(w, h, 1, ((255, 160, 90), (255, 226, 165)), L1)),
    ("bg.jpg", 1920, 1080, "agriculture,landscape", lambda w, h: landscape(w, h, 2, ((70, 130, 190), (190, 220, 235)), [(100, 160, 70), (80, 145, 60), (60, 125, 50), (45, 105, 40)])),
    ("leaf.jpg", 900, 700, "green,leaf", lambda w, h: leaf_image(w, h, "healthy", 3)),
    ("disease.jpg", 800, 600, "leaf,closeup", lambda w, h: leaf_image(w, h, "blight", 4)),
    ("weather.jpg", 1600, 600, "sky,clouds", lambda w, h: landscape(w, h, 5, ((40, 90, 160), (150, 195, 230)), [(70, 120, 70), (50, 100, 55)], n_clouds=14, sy=.22)),
    ("irrigation.jpg", 800, 600, "irrigation", lambda w, h: landscape(w, h, 6, ((90, 160, 220), (200, 230, 245)), [(80, 150, 65), (60, 130, 55), (50, 110, 45)], row_col=(80, 170, 230, 160))),
    ("yield.jpg", 800, 600, "harvest,grain", lambda w, h: crop_image("wheat", w, h)),
    ("fertilizer.jpg", 1600, 600, "soil,farming", lambda w, h: landscape(w, h, 7, ((120, 170, 210), (230, 215, 185)), [(120, 95, 60), (100, 75, 45), (85, 62, 38)], row_col=(40, 25, 10, 110))),
    ("advisor.jpg", 1600, 600, "farmland,crops", lambda w, h: landscape(w, h, 8, ((90, 160, 220), (210, 235, 240)), [(110, 170, 70), (80, 150, 55), (60, 130, 45), (45, 110, 40)])),
    ("history.jpg", 1600, 600, "farmer", lambda w, h: landscape(w, h, 9, ((110, 60, 120), (255, 150, 90)), [(70, 70, 50), (50, 55, 40), (35, 40, 30)], sun_col=(255, 190, 110), sy=.55)),
    ("library.jpg", 1600, 600, "plants,leaves", lambda w, h: leaf_image(w, h, "healthy", 10, count=3)),
    ("models.jpg", 1600, 600, "tractor", lambda w, h: landscape(w, h, 11, ((10, 30, 60), (20, 90, 100)), [(20, 60, 45), (15, 48, 36), (10, 36, 28)], sun_col=(230, 240, 255), row_col=(52, 211, 153, 70), sy=.25)),
    ("healthy.jpg", 800, 500, "fresh,leaf", lambda w, h: leaf_image(w, h, "healthy", 12)),
    ("blight.jpg", 800, 500, "dry,leaf", lambda w, h: leaf_image(w, h, "blight", 13)),
    ("rust.jpg", 800, 500, "rust,leaf", lambda w, h: leaf_image(w, h, "rust", 14)),
    ("mildew.jpg", 800, 500, "mildew", lambda w, h: leaf_image(w, h, "mildew", 15)),
    ("spot.jpg", 800, 500, "leaf,spots", lambda w, h: leaf_image(w, h, "spot", 16)),
    ("wheat.jpg", 400, 400, "wheat", lambda w, h: crop_image("wheat", w, h)),
    ("rice.jpg", 400, 400, "rice,paddy", lambda w, h: crop_image("rice", w, h)),
    ("maize.jpg", 400, 400, "corn,field", lambda w, h: crop_image("maize", w, h)),
    ("cotton.jpg", 400, 400, "cotton,plant", lambda w, h: crop_image("cotton", w, h)),
    ("sugarcane.jpg", 400, 400, "sugarcane", lambda w, h: crop_image("sugarcane", w, h)),
]

# ======================= MAIN =======================
def valid(p):
    try:
        if os.path.getsize(p) < 5000:
            return False
        with Image.open(p) as im:
            im.verify()
        return True
    except Exception:
        return False

def download(tags, w, h, lock, path):
    url = f"https://loremflickr.com/{w}/{h}/{tags}?lock={lock}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read()
    im = Image.open(io.BytesIO(data)).convert("RGB")
    if im.width < 300:
        raise ValueError("bad image")
    im.save(path, "JPEG", quality=88)

print("=" * 52)
print("   AgriMind AI - Preparing Website Images")
print("=" * 52)
online, fails = not OFFLINE, 0
for i, (name, w, h, tags, gen) in enumerate(JOBS):
    path = os.path.join(OUT, name)
    if not FORCE and valid(path):
        print(f"  [SKIP] {name} (already exists)")
        continue
    if online:
        try:
            download(tags, w, h, 11 + i, path)
            print(f"  [WEB]  {name}")
            fails = 0
            continue
        except Exception:
            fails += 1
            if fails >= 2:
                online = False
                print("  >> Internet download not working, switching to built-in image generator")
    gen(w, h).convert("RGB").save(path, "JPEG", quality=90)
    print(f"  [ART]  {name}")
print("=" * 52)
print(f"   Done! {len(JOBS)} images ready in {OUT}")
print("=" * 52)
