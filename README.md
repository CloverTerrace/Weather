# Home Weather Station Dashboard

A minimal GitHub Pages site that shows near-live conditions from your Ecowitt
station via the Weather Underground API — no server, no CORS issues, no
paid hosting.

## How it works

1. `scripts/fetch_weather.py` calls the Weather Underground PWS "current
   conditions" API for your station and saves the result to
   `data/weather.json`.
2. `.github/workflows/update-weather.yml` runs that script every 10 minutes
   (and on demand) and commits the updated file back to the repo.
3. `index.html` fetches `data/weather.json` directly — since it's served
   from the same GitHub Pages domain, there's no CORS problem, and it's
   nearly instant to load.

## Setup

1. **Create the repo.** Push these files to a new GitHub repository
   (public or private both work, but Pages on a free plan requires public
   unless you have GitHub Pro/Team/Enterprise).

2. **Get a Weather Underground API key** (free) at
   https://www.wunderground.com/member/api-keys — log in with the account
   linked to your station.

3. **Find your Station ID.** This is the ID you already use when uploading
   data from your Ecowitt console/gateway to Weather Underground (looks
   like `KPASOMEW3`).

4. **Add two repository secrets:**
   Go to your repo → Settings → Secrets and variables → Actions → New
   repository secret, and add:
   - `WU_STATION_ID` — your station ID
   - `WU_API_KEY` — your API key

5. **Enable GitHub Pages:**
   Settings → Pages → Source: "Deploy from a branch" → select `main` and
   `/ (root)`.

6. **Run the workflow once manually** to generate the first
   `data/weather.json`: go to the Actions tab → "Update Weather Data" →
   "Run workflow". After that it'll run automatically every 10 minutes.

7. Visit your Pages URL (something like
   `https://yourusername.github.io/your-repo-name/`) and you should see
   your live conditions.

## Customizing

- **Which fields show up, and their order/labels:** edit the `FIELDS`
  array near the top of the `<script>` block in `index.html`.
- **Colors/fonts:** edit the CSS variables at the top of `index.html`
  (`--bg-color`, `--accent-color`, etc.).
- **Update frequency:** change the cron schedule in
  `.github/workflows/update-weather.yml` (GitHub's minimum practical
  interval is about 5 minutes; note that scheduled workflows can be
  delayed further during periods of high GitHub Actions load).
- **Metric units:** change `units=e` to `units=m` in
  `scripts/fetch_weather.py`'s URL, and update the unit labels in
  `index.html` accordingly (°C, km/h, mm, hPa).

## Notes on Findu.com as an alternative source

Findu.com doesn't offer a clean, stable JSON API the way Weather
Underground does — it's built around APRS packet data and mostly returns
HTML or loosely-structured text/XML, which is more brittle to parse and
more likely to break silently. Since your station already reports to WU,
that's the more reliable pull source for this setup.
