import requests
from datetime import datetime
import os
from PIL import Image
from io import BytesIO
import re

# Output directories
OUTPUT_DIR = "output"
RAW_DIR = os.path.join(OUTPUT_DIR, "raw")
PROCESSED_DIR = os.path.join(OUTPUT_DIR, "processed")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Map of newspapers → Freedom Forum slugs
newspapers = {
    "wsj": "wsj",                # Wall Street Journal (NY)
    "nyt": "ny_nyt",             # New York Times (NY)
    "washpost": "dc_wp",         # Washington Post (Washington DC)
    "peoplesdaily": "chi_pd",    # People's Daily (Beijing)
    "chinadaily": "chi_cd",      # China Daily (Beijing)
    "lianhezaobao": "sing_lz",   # Lianhe Zaobao (Singapore)
}

# Today's date (YYYY-MM-DD)
today = datetime.now().strftime("%Y-%m-%d")

# Target resolution for Spectra 6 display (portrait)
TARGET_SIZE = (480, 800)

def autocrop_white_borders(img, tol=240, border_left=10, border_top=30, border_right=10, border_bottom=10):
    gray = img.convert("L")
    mask = gray.point(lambda x: 0 if x > tol else 255, '1')
    bbox = mask.getbbox()
    if not bbox:
        return img
    left = max(bbox[0] - border_left, 0)
    top = max(bbox[1] - border_top, 0)
    right = min(bbox[2] + border_right, img.width)
    bottom = min(bbox[3] + border_bottom, img.height)
    return img.crop((left, top, right, bottom))

def resize_and_crop(img, target_size):
    target_w, target_h = target_size
    img_ratio = img.width / img.height
    target_ratio = target_w / target_h
    if img_ratio > target_ratio:
        # Wider → squeeze horizontally
        print("📐 Image wider than target → squeezing to fit")
        return img.resize((target_w, target_h), Image.LANCZOS)
    else:
        # Taller → scale proportionally, crop from bottom
        print("📐 Image taller than target → scaling and cropping bottom")
        scale = target_w / img.width
        new_w = target_w
        new_h = int(img.height * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        top = 0
        bottom = min(new_h, target_h)
        return img.crop((0, top, new_w, bottom))

# --- NEW: cleanup helper ---
_DATE_RE = re.compile(r".*_(\d{4}-\d{2}-\d{2})\.jpg$", re.IGNORECASE)

def cleanup_raw_keep_latest_n(n_keep: int = 3):
    """Keep only the latest N calendar dates of raw images; delete older ones."""
    if not os.path.isdir(RAW_DIR):
        return
    # Collect files by date
    date_to_files = {}
    for fname in os.listdir(RAW_DIR):
        m = _DATE_RE.match(fname)
        if not m:
            continue
        date_str = m.group(1)
        date_to_files.setdefault(date_str, []).append(fname)
    if not date_to_files:
        return

    # Sort dates ascending and pick the newest n_keep
    sorted_dates = sorted(date_to_files.keys())  # YYYY-MM-DD sorts lexicographically
    keep_dates = set(sorted_dates[-n_keep:])

    # Delete files from older dates
    deleted = 0
    for d, files in date_to_files.items():
        if d in keep_dates:
            continue
        for f in files:
            path = os.path.join(RAW_DIR, f)
            try:
                os.remove(path)
                deleted += 1
            except Exception as e:
                print(f"⚠️ Failed to delete {path}: {e}")
    if deleted:
        print(f"🧹 Cleanup: removed {deleted} old raw file(s), kept dates: {', '.join(sorted(keep_dates))}")
    else:
        print(f"🧹 Cleanup: nothing to delete; kept dates: {', '.join(sorted(keep_dates))}")

# --- main fetch/process loop ---
for name, slug in newspapers.items():
    url = f"https://d2dr22b2lm4tvw.cloudfront.net/{slug}/{today}/front-page-large.jpg"
    print(f"Fetching {name}: {url}")

    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            img = Image.open(BytesIO(r.content))

            # Save raw image (JPG, original size)
            raw_path = os.path.join(RAW_DIR, f"{name}_{today}.jpg")
            img.save(raw_path, format="JPEG", quality=95, optimize=True)
            print(f"💾 Saved raw image → {raw_path}")

            # Convert to RGB and process
            img = img.convert("RGB")
            img = autocrop_white_borders(img, tol=240,
                                         border_left=10, border_top=30,
                                         border_right=10, border_bottom=10)
            processed_img = resize_and_crop(img, TARGET_SIZE)

            # Save processed (PNG, fixed name)
            proc_path = os.path.join(PROCESSED_DIR, f"{name}.png")
            processed_img.save(proc_path, format="PNG", optimize=True)
            print(f"✅ Saved processed image → {proc_path}")
        else:
            print(f"⚠ Failed to fetch {name} (status {r.status_code})")

    except Exception as e:
        print(f"❌ Error fetching {name}: {e}")

# --- NEW: run cleanup at the end ---
cleanup_raw_keep_latest_n(n_keep=3)
