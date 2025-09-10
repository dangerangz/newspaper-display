import requests
from datetime import datetime
import os

# Output directory
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Map of newspapers → Freedom Forum slugs
newspapers = {
    "wsj": "wsj",             # Wall Street Journal (NY)
    "nyt": "ny_nyt",             # New York Times (NY)
    "washpost": "dc_wp",  # Washington Post (Washington DC)
    "peoplesdaily": "chi_pd", # People's Daily (Beijing)
    "chinadaily": "chi_cd",     # China Daily (Beijing)
    "lianhezaobao": "sing_lz", # Lianhe Zaobao (Singapore)
}

# Today's date (YYYY-MM-DD)
today = datetime.now().strftime("%Y-%m-%d")

for name, slug in newspapers.items():
    # Construct the high-res image URL
    url = f"https://d2dr22b2lm4tvw.cloudfront.net/{slug}/{today}/front-page-large.jpg"
    print(f"Fetching {name}: {url}")

    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            filepath = os.path.join(OUTPUT_DIR, f"{name}.jpg")
            with open(filepath, "wb") as f:
                f.write(r.content)
            print(f"✅ Saved {filepath}")
        else:
            print(f"⚠ Failed to fetch {name} (status {r.status_code})")

    except Exception as e:
        print(f"❌ Error fetching {name}: {e}")
