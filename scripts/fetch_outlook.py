#!/usr/bin/env python3
"""
Downloads the current SPC (Storm Prediction Center) Day 1 Convective
Outlook image and saves it to data/outlook.png.

SPC issues several Day 1 outlooks per day (roughly 0600, 1300, 1630, and
2000 UTC), and each issuance gets its own timestamped filename (e.g.
day1otlk_1630.png) — there's no single permanently-current URL to hotlink.
So instead, this script reads SPC's own "current outlook" page each run
to find whichever image is actually current right now, then downloads it.
The image is always re-saved as data/outlook.png regardless of the
source file's actual format, so the page never needs to care what SPC
happens to be calling it.
"""

import io
import os
import re
import sys
import urllib.request
import urllib.error

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow is required. Add 'pip install pillow' to the workflow.", file=sys.stderr)
    sys.exit(1)

OUTLOOK_PAGE_URL = "https://www.spc.noaa.gov/products/outlook/day1otlk.html"
BASE_URL = "https://www.spc.noaa.gov/products/outlook/"
USER_AGENT = "(home-weather-station-dashboard, https://cloverterrace.github.io/Weather/)"


def fetch_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_bytes(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def find_current_image_url(page_html):
    # Look for an <img> tag whose src references the day1 outlook graphic
    # (e.g. "day1otlk_1630.gif" or "day1otlk_1630.png").
    match = re.search(r'src=["\']([^"\']*day1otlk[^"\']*\.(?:gif|png|jpg))["\']', page_html, re.IGNORECASE)
    if not match:
        return None

    src = match.group(1)
    if src.startswith("http"):
        return src
    return BASE_URL + src.lstrip("/")


def main():
    try:
        page_html = fetch_text(OUTLOOK_PAGE_URL)
    except Exception as e:
        print(f"Error fetching SPC outlook page: {e}", file=sys.stderr)
        sys.exit(1)

    image_url = find_current_image_url(page_html)
    if not image_url:
        print("ERROR: Could not find a current outlook image URL on the SPC page.", file=sys.stderr)
        sys.exit(1)

    print(f"Found current outlook image URL: {image_url}")

    try:
        image_bytes = fetch_bytes(image_url)
    except Exception as e:
        print(f"Error downloading outlook image: {e}", file=sys.stderr)
        sys.exit(1)

    # Normalize to PNG so the page always references the same known
    # filename/format, no matter what SPC names the source file.
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        print(f"Error decoding outlook image: {e}", file=sys.stderr)
        sys.exit(1)

    os.makedirs("data", exist_ok=True)
    img.save("data/outlook.png")
    print(f"Saved data/outlook.png (from {image_url})")


if __name__ == "__main__":
    main()
