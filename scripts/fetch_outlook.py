#!/usr/bin/env python3
"""
Downloads the current SPC (Storm Prediction Center) Day 1, Day 2, and
Day 3 Convective Outlook images and saves them to:
  data/outlook-day1.png
  data/outlook-day2.png
  data/outlook-day3.png

Each SPC outlook is issued at a handful of known times daily, and each
issuance's image lives at a filename tied to that time slot (e.g.
day1otlk_1630.png). These get overwritten in place at the same time the
next day — there's no single permanently-current URL — so this tries
the known candidate times directly, most recent first, and uses
whichever one actually loads successfully.
"""

import io
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow is required. Add 'pip install pillow' to the workflow.", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://www.spc.noaa.gov/products/outlook/"
USER_AGENT = "(home-weather-station-dashboard, https://cloverterrace.github.io/Weather/)"
EXTENSIONS = ["png", "gif"]

# Each day's known SPC issuance times (UTC, HHMM as int), most recent
# first within a day. Day 2's early issuance is listed as both 0600 and
# 0700 to cover the CST/CDT ambiguity in SPC's published schedule.
OUTLOOKS = [
    {"key": "day1", "prefix": "day1otlk", "times": [2000, 1630, 1300, 600, 100]},
    {"key": "day2", "prefix": "day2otlk", "times": [1730, 700, 600]},
    {"key": "day3", "prefix": "day3otlk", "times": [1930, 730]},
]


def candidate_urls(prefix, times):
    utc_now = datetime.now(timezone.utc)
    current_hhmm = utc_now.hour * 100 + utc_now.minute

    ordered_times = [t for t in times if current_hhmm >= t]
    # Fallback to yesterday's times too, in case today's hasn't posted yet.
    ordered_times += times

    for t in ordered_times:
        for ext in EXTENSIONS:
            yield f"{BASE_URL}{prefix}_{t:04d}.{ext}"


def try_fetch(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            if len(data) > 500:  # sanity check — a real image, not a tiny error page
                return data
    except (urllib.error.HTTPError, urllib.error.URLError):
        return None
    except Exception:
        return None
    return None


def fetch_one(key, prefix, times):
    for url in candidate_urls(prefix, times):
        print(f"[{key}] Trying {url} ...")
        image_bytes = try_fetch(url)
        if image_bytes:
            try:
                img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            except Exception as e:
                print(f"[{key}] Downloaded but couldn't decode, trying next: {e}", file=sys.stderr)
                continue

            os.makedirs("data", exist_ok=True)
            out_path = f"data/outlook-{key}.png"
            img.save(out_path)
            print(f"[{key}] Saved {out_path} (from {url})")
            return True

    print(f"[{key}] ERROR: no candidate URL loaded successfully.", file=sys.stderr)
    return False


def main():
    any_failed = False
    for outlook in OUTLOOKS:
        success = fetch_one(outlook["key"], outlook["prefix"], outlook["times"])
        if not success:
            any_failed = True

    if any_failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
