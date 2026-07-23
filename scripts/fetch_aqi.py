#!/usr/bin/env python3
"""
Fetches current US AQI (Air Quality Index) and pollutant levels for zip
15001 (Aliquippa, PA) from the free, no-key Open-Meteo Air Quality API,
and saves a simplified version to data/aqi.json.
"""

import json
import os
import sys
import urllib.request
import urllib.error

LATITUDE = 40.604
LONGITUDE = -80.286

URL = (
    "https://air-quality-api.open-meteo.com/v1/air-quality"
    f"?latitude={LATITUDE}&longitude={LONGITUDE}"
    "&current=us_aqi,pm2_5,pm10,ozone"
    "&timezone=auto"
)

USER_AGENT = "(home-weather-station-dashboard, https://cloverterrace.github.io/Weather/)"


def aqi_category(aqi):
    if aqi is None:
        return "Unknown"
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Moderate"
    if aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    if aqi <= 200:
        return "Unhealthy"
    if aqi <= 300:
        return "Very Unhealthy"
    return "Hazardous"


def main():
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.load(resp)
    except Exception as e:
        print(f"Error fetching air quality data: {e}", file=sys.stderr)
        sys.exit(1)

    current = data.get("current", {})
    us_aqi = current.get("us_aqi")

    output = {
        "time": current.get("time"),
        "us_aqi": us_aqi,
        "category": aqi_category(us_aqi),
        "pm2_5": current.get("pm2_5"),
        "pm10": current.get("pm10"),
        "ozone": current.get("ozone"),
    }

    os.makedirs("data", exist_ok=True)
    with open("data/aqi.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Wrote data/aqi.json: US AQI {us_aqi} ({output['category']})")


if __name__ == "__main__":
    main()
