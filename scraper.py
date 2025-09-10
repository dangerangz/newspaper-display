import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from datetime import datetime

# Output directory
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define target newspapers with identifiers and filenames
newspapers = {
    "wsj": ("https://frontpages.freedomforum.org/newspapers/wsj-The_Wall_Street_Journal", "wsj.png"),
    "nyt": ("https://frontpages.freedomforum.org/newspapers/ny_nyt-The_New_York_Times", "nyt.png"),
    "wp": ("https://frontpages.freedomforum.org/newspapers/dc_wp-The_Washington_Post", "wp.png"),
    "pd": ("https://frontpages.freedomforum.org/newspapers/chi_pd-People%E2%80%99s_Daily", "pd.png"),
    "cd": ("https://frontpages.freedomforum.org/newspapers/chi_cd-China_Daily", "cd.png"),
    "lhzb": ("https://frontpages.freedomforum.org/newspapers/sing_lz-Lianhe_Zaobao", "lhzb.png"),
    "st": ("https://e-paper.sph.com.sg/st", "st.png"),
    # Add more here as needed:
    # "people": ("https://frontpages.freedomforum.org/newspapers/...-People's_Daily", "people.png"),
    # etc.
}

for key, (url, filename) in newspapers.items():
    try:
        print(f"Fetching {key} from {url}")
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Find the main image tag
        img_tag = soup.find('img')
        if not img_tag or not img_tag.get('src'):
            print(f"⚠ No image found for {key}")
            continue

        img_url = img_tag['src']
        # Some src may be relative; make absolute if needed
        if img_url.startswith('/'):
            img_url = requests.compat.urljoin(url, img_url)

        print(f"Downloading image from {img_url}")
        img_bytes = requests.get(img_url).content
        img = Image.open(BytesIO(img_bytes))

        # Optional: resize/crop to e-ink resolution (e.g., 600×400)
        #img = img.convert("L")  # grayscale
        img = img.resize((400, 600))

        filepath = os.path.join(OUTPUT_DIR, filename)
        img.save(filepath)
        print(f"Saved to {filepath}")

    except Exception as e:
        print(f"Error processing {key}: {e}")
