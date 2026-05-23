#!/usr/bin/env python3
"""
Daily scraper: fetches librarian / library media specialist jobs in the Bay Area
from calopps.org, governmentjobs.com, and edjoin.org.

Writes ../data/jobs.json (current open jobs) and ../data/seen.json (first-seen
ledger for the "new today" badge).
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timezone
from html import unescape
from pathlib import Path
from typing import Iterable

import requests

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
HEADERS = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Inner Bay counties (per user selection). Used to filter results.
INNER_BAY_COUNTIES = {
    "San Francisco", "San Mateo", "Santa Clara",
    "Alameda", "Contra Costa", "Marin",
}

# Cities/agencies that map to those counties (used when an item only gives a city
# or a region tag). Keys are lowercase substrings; values are the county.
CITY_TO_COUNTY = {
    # San Francisco County
    "san francisco": "San Francisco",
    # San Mateo County
    "san mateo": "San Mateo", "daly city": "San Mateo", "redwood city": "San Mateo",
    "south san francisco": "San Mateo", "burlingame": "San Mateo", "menlo park": "San Mateo",
    "foster city": "San Mateo", "millbrae": "San Mateo", "belmont": "San Mateo",
    "san bruno": "San Mateo", "pacifica": "San Mateo", "half moon bay": "San Mateo",
    "east palo alto": "San Mateo", "san carlos": "San Mateo", "atherton": "San Mateo",
    "brisbane": "San Mateo", "hillsborough": "San Mateo", "portola valley": "San Mateo",
    "woodside": "San Mateo", "colma": "San Mateo",
    # Santa Clara County
    "santa clara": "Santa Clara", "san jose": "Santa Clara", "palo alto": "Santa Clara",
    "mountain view": "Santa Clara", "sunnyvale": "Santa Clara", "cupertino": "Santa Clara",
    "los gatos": "Santa Clara", "campbell": "Santa Clara", "milpitas": "Santa Clara",
    "gilroy": "Santa Clara", "morgan hill": "Santa Clara", "saratoga": "Santa Clara",
    "los altos": "Santa Clara", "monte sereno": "Santa Clara",
    # Alameda County
    "oakland": "Alameda", "berkeley": "Alameda", "fremont": "Alameda",
    "hayward": "Alameda", "alameda": "Alameda", "san leandro": "Alameda",
    "livermore": "Alameda", "pleasanton": "Alameda", "dublin": "Alameda",
    "union city": "Alameda", "newark": "Alameda", "emeryville": "Alameda",
    "albany": "Alameda", "piedmont": "Alameda", "castro valley": "Alameda",
    # Contra Costa County
    "richmond": "Contra Costa", "concord": "Contra Costa", "antioch": "Contra Costa",
    "walnut creek": "Contra Costa", "san ramon": "Contra Costa", "pittsburg": "Contra Costa",
    "brentwood": "Contra Costa", "danville": "Contra Costa", "martinez": "Contra Costa",
    "pleasant hill": "Contra Costa", "el cerrito": "Contra Costa", "hercules": "Contra Costa",
    "lafayette": "Contra Costa", "orinda": "Contra Costa", "moraga": "Contra Costa",
    "pinole": "Contra Costa", "san pablo": "Contra Costa", "oakley": "Contra Costa",
    # Marin County
    "san rafael": "Marin", "novato": "Marin", "mill valley": "Marin",
    "tiburon": "Marin", "sausalito": "Marin", "larkspur": "Marin",
    "corte madera": "Marin", "fairfax": "Marin", "ross": "Marin",
    "belvedere": "Marin",
}

# CalOpps tags its postings with a region; map those to counties.
CALOPPS_REGION_TO_COUNTIES = {
    "San Francisco/Peninsula": {"San Francisco", "San Mateo"},
    "South Bay": {"Santa Clara"},
    "East Bay": {"Alameda", "Contra Costa"},
    "North Bay": {"Marin"},  # also Sonoma/Napa/Solano, but those are out of scope
}

KEYWORDS = ["librarian", "library media specialist"]

# Title regex used to confirm a posting is actually a library role. CalOpps
# multi-word search doesn't filter server-side, and governmentjobs occasionally
# returns adjacent roles ("Records Specialist" etc.), so we double-check titles.
LIBRARY_TITLE_RE = re.compile(
    r"\b(librar(?:y|ian|ies)|media specialist|media tech|literacy)\b", re.I,
)


@dataclass
class Job:
    source: str
    source_id: str  # stable id from source (used for dedupe)
    title: str
    agency: str
    location: str
    county: str | None
    url: str
    salary: str = ""
    employment_type: str = ""
    closes: str = ""  # human string like "Closes in 1 week" or a date
    closes_date: str | None = None  # ISO date if parseable
    posted_date: str | None = None  # ISO date if known
    first_seen: str = ""  # filled in by main()


# ---------- helpers ---------------------------------------------------------

def clean(html: str) -> str:
    return unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html))).strip()


def infer_county(*texts: str) -> str | None:
    """Look at several text fields and figure out which Inner Bay county applies.

    Pass `texts` in priority order — typically (agency, location, region). A
    city match in the agency name beats any match found in a later (less
    specific) field. This handles the tricky case where agency = "City of Daly
    City" but the CalOpps region label is "San Francisco/Peninsula" — Daly City
    sits in San Mateo county and should win.
    """
    for text in texts:
        if not text:
            continue
        lower = text.lower()
        best: tuple[int, str] | None = None
        for city, county in CITY_TO_COUNTY.items():
            if re.search(rf"\b{re.escape(city)}\b", lower):
                if best is None or len(city) > best[0]:
                    best = (len(city), county)
        if best:
            return best[1]
        for c in INNER_BAY_COUNTIES:
            if re.search(rf"\b{re.escape(c.lower())}\b", lower):
                return c
    return None


def parse_neogov_date(s: str) -> str | None:
    """Parse /Date(1779408000000)/ to ISO date."""
    m = re.search(r"/Date\((-?\d+)\)/", s or "")
    if not m:
        return None
    ms = int(m.group(1))
    if ms < 0:  # sentinel "no date"
        return None
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).date().isoformat()


# ---------- calopps.org -----------------------------------------------------

def fetch_calopps(keyword: str) -> list[Job]:
    url = f"https://www.calopps.org/job-search/{urllib.parse.quote(keyword)}?keyword={urllib.parse.quote(keyword)}"
    out: list[Job] = []
    page = 0
    while True:
        page_url = f"{url}&page={page}" if page else url
        r = requests.get(page_url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        html = r.text
        blocks = re.findall(
            r'<div class="media search-result">(.*?)(?=<div class="media search-result">|<ul class="pager|<nav)',
            html, re.S,
        )
        if not blocks:
            break
        for block in blocks:
            title_m = re.search(
                r'<h3 class="media-heading">\s*<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',
                block,
            )
            if not title_m:
                continue
            job_url = title_m.group(1)
            raw_title = clean(title_m.group(2))
            # Strip trailing "(20740488)" id suffix
            title = re.sub(r"\s*\(\d+\)\s*$", "", raw_title)
            id_m = re.search(r"job-(\d+)", job_url)
            source_id = id_m.group(1) if id_m else job_url

            agency_m = re.search(r'<div class="meta-info">([^<]+)</div>', block)
            agency = clean(agency_m.group(1)) if agency_m else ""

            # Meta info: region, employment type, salary
            region_m = re.search(
                r'glyphicon-map-marker[^>]*></span>\s*<span[^>]*>([^<]+)</span>', block,
            )
            region = clean(region_m.group(1)) if region_m else ""

            etype_m = re.search(
                r'glyphicon-hourglass[^>]*></span>\s*<span[^>]*>([^<]+)</span>', block,
            )
            etype = clean(etype_m.group(1)) if etype_m else ""

            salary_m = re.search(r'class="a-salary">([^<]+)</span>', block)
            salary = clean(salary_m.group(1)) if salary_m else ""

            # CalOpps multi-word search doesn't filter, so we must confirm.
            if not LIBRARY_TITLE_RE.search(title):
                continue
            if region and region not in {
                "San Francisco/Peninsula", "South Bay", "East Bay", "North Bay",
            }:
                continue

            county = infer_county(agency, region)
            # If region narrows to multiple inner-bay counties, pick the agency-matched one
            if not county and region in CALOPPS_REGION_TO_COUNTIES:
                inner = CALOPPS_REGION_TO_COUNTIES[region] & INNER_BAY_COUNTIES
                if inner and len(inner) == 1:
                    county = next(iter(inner))
                elif inner:
                    # Best-guess: pick alphabetically first to keep stable.
                    county = sorted(inner)[0]
            if county not in INNER_BAY_COUNTIES:
                continue

            out.append(Job(
                source="calopps",
                source_id=f"calopps-{source_id}",
                title=title,
                agency=agency,
                location=region,
                county=county,
                url=job_url,
                salary=salary,
                employment_type=etype,
            ))

        # Pagination — only continue if there's a next-page link
        if f'page={page + 1}' not in html:
            break
        page += 1
        if page > 10:  # safety
            break
        time.sleep(0.5)
    return out


# ---------- governmentjobs.com ---------------------------------------------

GJ_BASE = (
    "https://www.governmentjobs.com/jobs"
    "?Keyword={kw}&Location={loc}"
    "&RemoteWorkOptionId=0&IsSchoolJobs=False&ShowRedesignedUI=False"
    "&IsEditClicked=False&IsFilterEmpty=False&CurrentFacetLimit=0"
    "&IsFeatured=False&IsSubmittedApplicationPage=False&Page={page}"
)


def fetch_governmentjobs(keyword: str) -> list[Job]:
    out: list[Job] = []
    # Query once per major county to keep relevance high. The site's location
    # filter accepts free-form "City, CA" or "County, CA".
    locations = [
        "San Francisco, CA", "San Mateo County, CA", "Santa Clara County, CA",
        "Alameda County, CA", "Contra Costa County, CA", "Marin County, CA",
    ]
    seen_ids: set[str] = set()
    for loc in locations:
        page = 1
        while True:
            url = GJ_BASE.format(
                kw=urllib.parse.quote(keyword),
                loc=urllib.parse.quote(loc),
                page=page,
            )
            r = requests.get(url, headers=HEADERS, timeout=30)
            r.raise_for_status()
            html = r.text
            # Each <li class="job-item" data-job-id="..."> block
            items = re.findall(
                r'<li class="job-item"\s+data-job-id="([^"]+)"[^>]*>(.*?)</li>',
                html, re.S,
            )
            if not items:
                break
            new_count = 0
            for jid, block in items:
                if jid in seen_ids:
                    continue
                title_m = re.search(
                    r'<a [^>]*class="job-details-link" href="([^"]+)">([^<]+)</a>',
                    block,
                )
                if not title_m:
                    continue
                title = clean(title_m.group(2))
                job_path = title_m.group(1)
                full_url = "https://www.governmentjobs.com" + job_path

                org_m = re.search(
                    r'class="primaryInfo job-organization">([^<]+)</div>', block,
                )
                agency = clean(org_m.group(1)) if org_m else ""

                locm = re.search(r'class="job-location">([^<]+)</span>', block)
                job_loc = clean(locm.group(1)) if locm else ""

                # Last <div class="primaryInfo"> holds "type | salary | closes".
                all_pi = re.findall(r'<div class="primaryInfo">\s*(.*?)\s*</div>', block, re.S)
                tail = clean(all_pi[-1]) if all_pi else ""
                parts = [p.strip() for p in tail.split("|")]
                etype = parts[0] if len(parts) >= 1 else ""
                salary = parts[1] if len(parts) >= 2 else ""
                closes = parts[2] if len(parts) >= 3 else ""

                if not LIBRARY_TITLE_RE.search(title):
                    continue

                # Must be in CA — gj sometimes leaks out-of-state results
                if ", CA" not in job_loc and "California" not in job_loc:
                    continue
                county = infer_county(agency, job_loc)
                if county not in INNER_BAY_COUNTIES:
                    continue

                seen_ids.add(jid)
                new_count += 1
                out.append(Job(
                    source="governmentjobs",
                    source_id=f"governmentjobs-{jid}",
                    title=title,
                    agency=agency,
                    location=job_loc,
                    county=county,
                    url=full_url,
                    salary=salary,
                    employment_type=etype,
                    closes=closes,
                ))

            if new_count == 0 and page > 1:
                break
            # Pagination — stop if no "Page X+1" link in HTML
            if f'Page={page + 1}' not in html and f'page={page + 1}' not in html:
                break
            page += 1
            if page > 8:
                break
            time.sleep(0.5)
    return out


# ---------- edjoin.org ------------------------------------------------------

EDJOIN_API = (
    "https://www.edjoin.org/Home/LoadJobs"
    "?rows=100&page=1&sort=postingDate&sortVal=0&order=desc"
    "&keywords={kw}&location=&searchType=all"
    "&regions=&jobTypes=&days=0&empType=&catID=0&onlineApps="
    "&recruitmentCenterID=0&stateID=0&regionID=0&districtID=0&searchID=0"
)


def fetch_edjoin(keyword: str) -> list[Job]:
    url = EDJOIN_API.format(kw=urllib.parse.quote(keyword))
    r = requests.get(
        url,
        headers={**HEADERS, "X-Requested-With": "XMLHttpRequest",
                 "Referer": f"https://www.edjoin.org/Home/Jobs?keywords={urllib.parse.quote(keyword)}"},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    out: list[Job] = []
    for j in data.get("data", []):
        county_name = (j.get("countyName") or "").strip()
        if county_name not in INNER_BAY_COUNTIES:
            continue
        pid = str(j.get("postingID"))
        title = clean(j.get("positionTitle") or "")
        agency = clean(j.get("districtName") or "")
        city = clean(j.get("city") or "")
        location = ", ".join(p for p in [city, county_name + " County"] if p)
        salary = clean(j.get("salaryInfo") or "")
        if not salary:
            lo, hi = j.get("PayRangeFrom") or "", j.get("PayRangeTo") or ""
            unit = j.get("PayRangeDropdown") or ""
            if lo and hi:
                salary = f"{lo} - {hi} {unit}".strip()
        ftpt = clean(j.get("FullTimePartTime") or "")
        posted = parse_neogov_date(j.get("postingDate") or "")
        closes = parse_neogov_date(j.get("displayUntil") or "")
        url_detail = f"https://www.edjoin.org/Home/JobPosting/{pid}"
        out.append(Job(
            source="edjoin",
            source_id=f"edjoin-{pid}",
            title=title,
            agency=agency,
            location=location,
            county=county_name,
            url=url_detail,
            salary=salary,
            employment_type=ftpt,
            closes=f"Closes {closes}" if closes else "",
            closes_date=closes,
            posted_date=posted,
        ))
    return out


# ---------- orchestrator ----------------------------------------------------

def fetch_all() -> list[Job]:
    fetchers = [
        ("calopps", fetch_calopps),
        ("governmentjobs", fetch_governmentjobs),
        ("edjoin", fetch_edjoin),
    ]
    all_jobs: dict[str, Job] = {}
    for name, fn in fetchers:
        for kw in KEYWORDS:
            try:
                jobs = fn(kw)
                print(f"  [{name}/{kw}] {len(jobs)} matches", file=sys.stderr)
                for j in jobs:
                    # Dedupe across keywords by source_id; keep first.
                    all_jobs.setdefault(j.source_id, j)
            except Exception as e:
                print(f"  [{name}/{kw}] ERROR: {e}", file=sys.stderr)
    return list(all_jobs.values())


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    seen_path = DATA_DIR / "seen.json"
    jobs_path = DATA_DIR / "jobs.json"

    today = date.today().isoformat()
    seen: dict[str, str] = {}
    if seen_path.exists():
        seen = json.loads(seen_path.read_text())

    jobs = fetch_all()
    print(f"Total unique jobs after dedupe: {len(jobs)}", file=sys.stderr)

    # Stamp first_seen and update seen.json
    for j in jobs:
        if j.source_id not in seen:
            seen[j.source_id] = today
        j.first_seen = seen[j.source_id]

    # Drop seen entries that have aged out (job no longer open) after 60 days
    current_ids = {j.source_id for j in jobs}
    cutoff = (date.today().toordinal() - 60)
    pruned_seen = {
        sid: d for sid, d in seen.items()
        if sid in current_ids or date.fromisoformat(d).toordinal() >= cutoff
    }

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "counties": sorted(INNER_BAY_COUNTIES),
        "keywords": KEYWORDS,
        "jobs": [asdict(j) for j in jobs],
    }
    jobs_path.write_text(json.dumps(payload, indent=2))
    seen_path.write_text(json.dumps(pruned_seen, indent=2, sort_keys=True))
    print(f"Wrote {jobs_path} ({len(jobs)} jobs)", file=sys.stderr)


if __name__ == "__main__":
    main()
