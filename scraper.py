import requests
from datetime import datetime
import os
from PIL import Image
from io import BytesIO

# Output directory
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

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

# Target resolution for your Spectra 6 display (portrait)
TARGET_SIZE = (480, 800)

def resize_and_crop(img, target_size):
    target_w, target_h = target_size
    img_ratio = img.width / img.height
    target_ratio = target_w / target_h

    # Scale image to fill the target box
    if img_ratio > target_ratio:
        # Image is wider → scale by height
        scale = target_h / img.height
    else:
        # Image is taller → scale by width
        scale = target_w / img.width

    new_w = int(img.width * scale)
    new_h = int(img.height * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)

    # Crop the image to fit target size
    left = max(0, (new_w - target_w) // 2)
    top = 0
    right = left + target_w
    bottom = top + target_h
    return img.crop((left, top, right, bottom))

for name, slug in newspapers.items():
    # Construct the high-res image URL
    url = f"https://d2dr22b2lm4tvw.cloudfront.net/{slug}/{today}/front-page-large.jpg"
    print(f"Fetching {name}: {url}")

    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            # Open image from bytes
            img = Image.open(BytesIO(r.content))

            # Convert to RGB (good for color e-ink displays like Spectra 6)
            img = img.convert("RGB")

            # Resize with crop/letterbox to 480x800
            img = resize_and_crop(img, TARGET_SIZE)

            # Save final image
            filepath = os.path.join(OUTPUT_DIR, f"{name}.jpg")
            img.save(filepath, format="JPEG", quality=90)
            print(f"✅ Saved {filepath}")
        else:
            print(f"⚠ Failed to fetch {name} (status {r.status_code})")

    except Exception as e:
        print(f"❌ Error fetching {name}: {e}")
