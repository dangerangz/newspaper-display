import requests
from datetime import datetime
import os
from PIL import Image
from io import BytesIO

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

def resize_and_crop(img, target_size):
    target_w, target_h = target_size
    img_ratio = img.width / img.height
    target_ratio = target_w / target_h

    if img_ratio > target_ratio:
        # Image is wider → squeeze horizontally to fit
        print("📐 Image wider than target → squeezing to fit")
        return img.resize((target_w, target_h), Image.LANCZOS)
    else:
        # Image is taller → scale proportionally, crop from bottom
        print("📐 Image taller than target → scaling and cropping bottom")
        scale = target_w / img.width
        new_w = target_w
        new_h = int(img.height * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)

        # Crop height if needed
        top = 0
        bottom = min(new_h, target_h)
        return img.crop((0, top, new_w, bottom))

for name, slug in newspapers.items():
    url = f"https://d2dr22b2lm4tvw.cloudfront.net/{slug}/{today}/front-page-large.jpg"
    print(f"Fetching {name}: {url}")

    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            # Open image from bytes
            img = Image.open(BytesIO(r.content))

            # Save RAW full image (JPG, original quality)
            raw_path = os.path.join(RAW_DIR, f"{name}_{today}.jpg")
            img.save(raw_path, format="JPEG", quality=95, optimize=True)
            print(f"💾 Saved raw image → {raw_path}")

            # Convert to RGB for color e-ink
            img = img.convert("RGB")

            # Resize to panel resolution
            processed_img = resize_and_crop(img, TARGET_SIZE)

            # Save processed version as PNG (lossless, sharp)
            proc_path = os.path.join(PROCESSED_DIR, f"{name}.png")
            processed_img.save(proc_path, format="PNG", optimize=True)
            print(f"✅ Saved processed image → {proc_path}")
        else:
            print(f"⚠ Failed to fetch {name} (status {r.status_code})")

    except Exception as e:
        print(f"❌ Error fetching {name}: {e}")
