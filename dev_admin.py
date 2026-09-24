import os, json, time
from PIL import Image, ImageOps
from flask import request, jsonify, session

LANCZOS = getattr(Image, "Resampling", Image).LANCZOS
DEFAULT = {"x": 0.5, "y": 0.4, "zoom": 0.8}
ALLOWED = (".jpg", ".jpeg", ".png", ".webp", ".bmp")


def paths(base):
    folder = os.path.join(base, "static", "img")
    os.makedirs(folder, exist_ok=True)
    return (os.path.join(folder, "developer.jpg"),
            os.path.join(folder, "developer_original.jpg"),
            os.path.join(folder, "developer.json"))


def load_cfg(base):
    try:
        with open(paths(base)[2], encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_cfg(base, cfg):
    with open(paths(base)[2], "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def crop_photo(base, x=None, y=None, zoom=None):
    out, orig, _ = paths(base)
    if not os.path.exists(orig):
        raise FileNotFoundError("Original photo not found. Upload a photo first.")
    cfg = load_cfg(base)
    x = _clamp(float(cfg.get("x", DEFAULT["x"]) if x is None else x), 0.0, 1.0)
    y = _clamp(float(cfg.get("y", DEFAULT["y"]) if y is None else y), 0.0, 1.0)
    zoom = _clamp(float(cfg.get("zoom", DEFAULT["zoom"]) if zoom is None else zoom), 0.15, 1.0)
    with Image.open(orig) as im:
        im = im.convert("RGB")
        w, h = im.size
        side = zoom * min(w, h)
        left = _clamp(x * w - side / 2, 0, w - side)
        top = _clamp(y * h - side / 2, 0, h - side)
        box = tuple(int(round(v)) for v in (left, top, left + side, top + side))
        im.crop(box).resize((600, 600), LANCZOS).save(out, "JPEG", quality=92, optimize=True)
    cfg.update(x=round(x, 4), y=round(y, 4), zoom=round(zoom, 4), v=int(time.time() * 1000))
    save_cfg(base, cfg)
    return cfg


def set_photo(base, src, x=None, y=None, zoom=None):
    _, orig, _ = paths(base)
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((1800, 1800), LANCZOS)
        im.save(orig, "JPEG", quality=92)
    return crop_photo(base,
                      DEFAULT["x"] if x is None else x,
                      DEFAULT["y"] if y is None else y,
                      DEFAULT["zoom"] if zoom is None else zoom)


def delete_photo(base):
    removed = False
    for p in paths(base)[:2]:
        if os.path.exists(p):
            os.remove(p)
            removed = True
    cfg = load_cfg(base)
    for k in ("x", "y", "zoom"):
        cfg.pop(k, None)
    cfg["v"] = int(time.time() * 1000)
    save_cfg(base, cfg)
    return removed


def photo_info(base):
    out, orig, _ = paths(base)
    cfg = load_cfg(base)
    exists = os.path.exists(out)
    return {"exists": exists, "has_original": os.path.exists(orig),
            "v": cfg.get("v", int(os.path.getmtime(out) * 1000) if exists else 0),
            "x": cfg.get("x", DEFAULT["x"]), "y": cfg.get("y", DEFAULT["y"]),
            "zoom": cfg.get("zoom", DEFAULT["zoom"])}


def init_dev_admin(app, db):
    base = app.root_path

    def can_edit():
        uid = session.get("uid")
        if not uid:
            return False
        with db() as c:
            u = c.execute("SELECT username FROM users WHERE id=?", (uid,)).fetchone()
            if not u or u["username"] == "demo":
                return False
            owner = load_cfg(base).get("owner")
            if owner:
                return u["username"] == owner
            first = c.execute("SELECT id FROM users WHERE username != 'demo' ORDER BY id LIMIT 1").fetchone()
        return bool(first and first["id"] == uid)

    def deny():
        return jsonify(ok=False, error="Only the developer account can change this photo."), 403

    def num(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    @app.route("/api/dev-photo", methods=["GET"])
    def dev_photo_info():
        return jsonify(ok=True, can_edit=can_edit(), **photo_info(base))

    @app.route("/api/dev-photo", methods=["POST"])
    def dev_photo_upload():
        if not can_edit():
            return deny()
        f = request.files.get("photo")
        if not f or not f.filename:
            return jsonify(ok=False, error="Please choose a photo."), 400
        if os.path.splitext(f.filename)[1].lower() not in ALLOWED:
            return jsonify(ok=False, error="Use a JPG, PNG or WEBP photo."), 400
        try:
            set_photo(base, f.stream, num(request.form.get("x")), num(request.form.get("y")), num(request.form.get("zoom")))
        except Exception as e:
            return jsonify(ok=False, error=f"Could not read image: {e}"), 400
        return jsonify(ok=True, can_edit=True, **photo_info(base))

    @app.route("/api/dev-photo/crop", methods=["POST"])
    def dev_photo_crop():
        if not can_edit():
            return deny()
        d = request.get_json(silent=True) or {}
        try:
            crop_photo(base, num(d.get("x")), num(d.get("y")), num(d.get("zoom")))
        except FileNotFoundError as e:
            return jsonify(ok=False, error=str(e)), 400
        return jsonify(ok=True, can_edit=True, **photo_info(base))

    @app.route("/api/dev-photo", methods=["DELETE"])
    def dev_photo_delete():
        if not can_edit():
            return deny()
        removed = delete_photo(base)
        return jsonify(ok=True, removed=removed, can_edit=True, **photo_info(base))

    print("Developer photo manager ready.")
