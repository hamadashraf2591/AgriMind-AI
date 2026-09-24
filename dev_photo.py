import os, sys, argparse
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from dev_admin import set_photo, crop_photo, delete_photo, photo_info, load_cfg, save_cfg

p = argparse.ArgumentParser(description="AgriMind AI - Developer photo manager")
p.add_argument("action", choices=["set", "edit", "delete", "info", "owner"])
p.add_argument("value", nargs="?", help="photo path (set) or username (owner)")
p.add_argument("--x", type=float, help="0-1 : 0 = left, 1 = right")
p.add_argument("--y", type=float, help="0-1 : 0 = top, 1 = bottom")
p.add_argument("--zoom", type=float, help="0.15-1 : smaller = closer")
a = p.parse_args()

print("=" * 56)
try:
    if a.action == "set":
        path = a.value
        if not path:
            try:
                import tkinter as tk
                from tkinter import filedialog
                r = tk.Tk(); r.withdraw(); r.attributes("-topmost", True)
                path = filedialog.askopenfilename(title="Select your photo",
                                                  filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.bmp")])
                r.destroy()
            except Exception:
                path = ""
        if not path or not os.path.exists(path):
            print("  [X] Photo not found:", path or "(nothing selected)")
            sys.exit(1)
        cfg = set_photo(BASE, path, a.x, a.y, a.zoom)
        print("  [OK] Photo set  ->  static/img/developer.jpg")
        print(f"       x={cfg['x']}  y={cfg['y']}  zoom={cfg['zoom']}")
    elif a.action == "edit":
        cfg = crop_photo(BASE, a.x, a.y, a.zoom)
        print(f"  [OK] Photo re-cropped: x={cfg['x']}  y={cfg['y']}  zoom={cfg['zoom']}")
    elif a.action == "delete":
        print("  [OK] Photo deleted (initials 'MH' will show)" if delete_photo(BASE) else "  [i] No photo to delete")
    elif a.action == "info":
        for k, v in photo_info(BASE).items():
            print(f"  {k:<13}: {v}")
        print(f"  {'owner':<13}: {load_cfg(BASE).get('owner', '(first account)')}")
    elif a.action == "owner":
        if not a.value:
            print("  [X] Usage: python dev_photo.py owner <username>")
            sys.exit(1)
        cfg = load_cfg(BASE); cfg["owner"] = a.value.strip().lower(); save_cfg(BASE, cfg)
        print(f"  [OK] Photo edit rights given to: {cfg['owner']}")
except FileNotFoundError as e:
    print("  [X]", e)
print("=" * 56)
