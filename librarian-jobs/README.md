# Bay Area Librarian Jobs

A static site that lists open librarian, library assistant, and school
library media specialist roles across the Inner Bay Area (SF, San Mateo,
Santa Clara, Alameda, Contra Costa, Marin), refreshed daily.

## Sources

- [calopps.org](https://www.calopps.org/) — city/county library jobs
- [governmentjobs.com](https://www.governmentjobs.com/) — broader public-sector
- [edjoin.org](https://www.edjoin.org/) — K-12 school library jobs

## Local use

```sh
pip install -r scraper/requirements.txt
python scraper/scrape.py        # writes data/jobs.json + data/seen.json
python -m http.server 8765      # open http://localhost:8765
```

## How daily updates work

`.github/workflows/librarian-jobs.yml` runs every day at 14:00 UTC (≈7am
Pacific). It runs the scraper, commits any changes to `data/jobs.json`, and
redeploys the site to GitHub Pages.

`data/seen.json` is a ledger that records the date each posting first
appeared, so the UI can flag "new today" without depending on the source
sites' own freshness metadata.

## To enable on GitHub

1. Push this repo to GitHub.
2. In **Settings → Pages**, set Source = "GitHub Actions".
3. The workflow will fire on its schedule and on demand from the Actions tab.

## Adjusting the search

- Counties: edit `INNER_BAY_COUNTIES` in `scraper/scrape.py`.
- Keywords: edit `KEYWORDS` in the same file.
- Cities → county mapping: extend `CITY_TO_COUNTY` if a posting from an
  unmapped Bay Area city gets dropped.
