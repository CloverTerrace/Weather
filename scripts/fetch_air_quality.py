#!/usr/bin/env python3
"""
Pulls the latest PM2.5 reading from a specific PurpleAir sensor, applies
the standard EPA AQI breakpoint table, and saves the result to
data/air_quality.json.

Uses the sensor's pm2.5_alt field, which PurpleAir returns with the
EPA/Barkjohn correction already applied — the same correction used by
AirNow's Fire and Smoke Map, tuned to stay accurate during wildfire smoke
rather than just clean-air conditions.
"""
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

SENSOR_INDEX = 308482
API_KEY = os.environ.get("PURPLEAIR_API_KEY")
API_URL = f"https://api.purpleair.com/v1/sensors/{SENSOR_INDEX}?fields=pm2.5_alt,humidity,last_seen,name"

# Standard US EPA PM2.5 AQI breakpoints: (pm_low, pm_high, aqi_low, aqi_high, category)
AQI_BREAKPOINTS = [
    (0.0, 12.0, 0, 50, "Good"),
    (12.1, 35.4, 51, 100, "Moderate"),
    (35.5, 55.4, 101, 150, "Unhealthy for Sensitive Groups"),
    (55.5, 150.4, 151, 200, "Unhealthy"),
    (150.5, 250.4, 201, 300, "Very Unhealthy"),
    (250.5, 350.4, 301, 400, "Hazardous"),
    (350.5, 500.4, 401, 500, "Hazardous"),
]


def pm25_to_aqi(pm25):
    pm25 = max(0.0, pm25)
    for pm_low, pm_high, aqi_low, aqi_high, category in AQI_BREAKPOINTS:
        if pm_low <= pm25 <= pm_high:
            aqi = ((aqi_high - aqi_low) / (pm_high - pm_low)) * (pm25 - pm_low) + aqi_low
            return round(aqi), category
    # Above the top breakpoint — cap display at 500+/Hazardous rather than erroring.
    return 500, "Hazardous"


def main():
    if not API_KEY:
        print("ERROR: PURPLEAIR_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    req = urllib.request.Request(API_URL, headers={"X-API-Key": API_KEY})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            payload = json.loads(resp.read())
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        print(f"ERROR: Failed to fetch PurpleAir data: {e}", file=sys.stderr)
        sys.exit(1)

    fields = payload["sensor"]
    pm25 = fields["pm2.5_alt"]
    aqi, category = pm25_to_aqi(pm25)

    result = {
        "aqi": aqi,
        "aqiCategory": category,
        "aqiDisplay": f"{aqi} ({category})",
        "pm25": round(pm25, 1),
        "humidity": fields.get("humidity"),
        "sensorLastSeen": datetime.fromtimestamp(fields["last_seen"], tz=timezone.utc).isoformat(),
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
    }

    os.makedirs("data", exist_ok=True)
    with open("data/air_quality.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"Saved data/air_quality.json — AQI {aqi} ({category})")


if __name__ == "__main__":
    main()
