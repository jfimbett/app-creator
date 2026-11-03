# SEC EDGAR APIs and fair access — implementation notes

All sources were retrieved on 2026-11-03. Source keys used below:

- **[API]** https://www.sec.gov/search-filings/edgar-application-programming-interfaces (copy at `/page/edgar-application-programming-interfaces-old` also fetched)
- **[AED]** https://www.sec.gov/os/accessing-edgar-data
- **[DEV]** https://www.sec.gov/about/developer-resources
- **[SEC-POL]** https://www.sec.gov/privacy.htm#security (Internet Security Policy)
- **[SAMPLE]** live responses, used for structure only: `data.sec.gov/api/xbrl/companyconcept/CIK0000320193/us-gaap/AccountsPayableCurrent.json`, `data.sec.gov/submissions/CIK0000320193.json` and `www.sec.gov/files/company_tickers.json`

Anything marked **[unverified]** was not found in an official page I fetched.

## 1. Hosts

- `data.sec.gov` hosts the "RESTful data APIs delivering JSON-formatted data" [API]. The APIs "do not require any authentication or API keys" [API].
- `www.sec.gov` hosts the filing archives, the indexes, the ticker files and the bulk ZIPs [AED][API].

## 2. Endpoints (data.sec.gov)

Every endpoint takes a 10-digit CIK "including leading zeros" [API].

| Purpose | URL pattern |
|---|---|
| Submissions | `https://data.sec.gov/submissions/CIK##########.json` |
| Company concept | `https://data.sec.gov/api/xbrl/companyconcept/CIK##########/{taxonomy}/{tag}.json` (example: `us-gaap/AccountsPayableCurrent`) |
| Company facts | `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json` |
| Frames | `https://data.sec.gov/api/xbrl/frames/{taxonomy}/{tag}/{unit}/{period}.json` (example: `us-gaap/AccountsPayableCurrent/USD/CY2019Q1I`) |

Source for all patterns: [API].

### Submissions

- Contents: "metadata such as current name, former name, and stock exchanges and ticker symbols of publicly-traded companies" [API].
- The recent-filings array holds "at least one year's of filing or to 1,000 (whichever is more) of the most recent filings in a compact columnar data array" [API].
- Pagination: "If the entity has additional filings, files will contain an array of additional JSON files and the date range for the filings each one contains" [API].
- The documentation does not spell out the JSON key names. They come from the live response [SAMPLE]:
  - `filings` has two keys, `recent` and `files`.
  - `recent` is columnar: parallel arrays such as `accessionNumber`, `filingDate`, `reportDate` and `primaryDocDescription`. Other columns, including `form`, `primaryDocument`, `acceptanceDateTime`, `isXBRL` and `isInlineXBRL`, are **[unverified]** because the fetch summarised that part of the response.
  - Each `files[]` entry has `name`, `filingCount`, `filingFrom` and `filingTo`, for example `CIK0000320193-submissions-001.json`.
  - Fetch each older page at `https://data.sec.gov/submissions/{name}`. That URL form is **[unverified]**, inferred from the naming.

### Company concept and company facts

- companyconcept "returns all the XBRL disclosures from a single company (CIK) and concept (a taxonomy and tag) into a single JSON file, with a separate array of facts for each units on measure" [API].
- companyfacts "returns all the company concepts data for a company into a single API call" [API].
- Field names are not documented on [API]. In the live response [SAMPLE]:
  - Top-level keys are `cik`, `taxonomy`, `tag`, `label`, `description`, `entityName` and `units`.
  - `units` is keyed by unit (for example `USD`), and each value is an array of fact objects.
  - A fact object has `end`, `val`, `accn`, `fy`, `fp`, `form` and `filed`. `frame` appears on some facts only. `start` appears on duration concepts; it is absent on instant concepts such as AccountsPayableCurrent. The presence of `start` on duration concepts is **[unverified]**.
- Units: a numerator and denominator are joined with "-per-" (for example "USD-per-shares"), and "the default unit in XBRL is 'pure'" [API].

### Frames

- A frame "aggregates one fact for each reporting entity that is last filed that most closely fits the calendrical period requested" [API].
- Period formats [API]:
  - `CY####` is annual data, with a duration of "365 days +/- 30 days".
  - `CY####Q#` is quarterly data, with a duration of "91 days +/- 30 days".
  - `CY####Q#I` is instantaneous data.
- "the frame data is assembled by the dates that best align with a calendar quarter or year. Data users should be mindful different reporting start and end dates for facts contained in a frame" [API].
- The `frame` field on a fact is the calendar frame that fact was chosen for, for example `"frame":"CY2013Q3I"` [SAMPLE].

### Why fy/fp are filing-level, not period-level

[API] has **no text** on this; the claim is **[unverified]** in the official documentation. The live data shows the behaviour [SAMPLE]:

- A fact for the period ending 2011-09-24 carries `fy: 2012, fp: "FY", form: "8-K", filed: "2013-04-24"`.
- A fact for the period ending 2013-09-28 has `fy: null, fp: null` and was filed on an 8-K.

So `fy`, `fp`, `form`, `filed` and `accn` describe the filing that reported the value. The same period recurs in later filings as a comparative figure.

Implementation rules:

- Identify a period by `start`/`end` (or by `frame`), never by `fy`/`fp`.
- Deduplicate on (`start`, `end`, unit), preferring the latest `filed`.

## 3. Ticker and CIK files (www.sec.gov)

All three files are documented in [AED]. [DEV] and [API] do not mention them.

- `https://www.sec.gov/files/company_tickers.json` is the "data file for ticker, CIK, EDGAR conformed company name associations".
  - Its structure [SAMPLE]: a JSON object keyed `"0"`, `"1"`, …, where each value is `{cik_str: int, ticker: str, title: str}`.
  - Pad `cik_str` to 10 digits for the data.sec.gov endpoints.
- `https://www.sec.gov/files/company_tickers_exchange.json` holds "EDGAR conformed company name, CIK, ticker, exchange associations". Its path moved from `/data/` to `/files/`, and a redirect is in place.
- `https://www.sec.gov/files/company_tickers_mf.json` holds mutual fund CIK, series, class and ticker associations.
- The files are updated "periodically", and the SEC does "not guarantee accuracy or scope". Treat the ticker mapping as best-effort.

## 4. Archive URL structure (www.sec.gov) [AED]

- Accession number format: 10-2-6 digits, for example `0001193125-15-118890`. The parts are the filer or filer-agent CIK, the 2-digit year and a sequence number.
- Example paths:
  - `/Archives/edgar/data/1122304/0001193125-15-118890.txt`
  - `/Archives/edgar/data/1122304/000119312515118890/0001193125-15-118890.txt`
  - `/Archives/edgar/data/1122304/0001193125-15-118890-index.html`
- Filings made after EDGAR 7.0 (May 26, 2000) are "also accessible via an alternative symbolic path, incorporating an intermediate accession-number directory without dashes".
- The practical document URL is therefore `https://www.sec.gov/Archives/edgar/data/<cik>/<accession-no-dashes>/<primaryDocument>`. Here `<cik>` has no leading zeros in the examples, and `primaryDocument` comes from the submissions columns. This composed pattern is **[unverified]** as a single documented URL.
- Directories and indexes:
  - "Directory browsing is allowed for CIK and accession-number directories", but `/Archives/edgar/data/` itself is not browsable.
  - Each CIK and accession directory has `index.html`, `index.xml` and `index.json`, which "are not visible through directory browsing".
  - Index files cover 1994Q3 to the present. `/Archives/edgar/full-index/` and `/Archives/edgar/daily-index/` each come in company, form, master and XBRL variants.

## 5. Fair access, User-Agent, rate limit

- **Rate limit:**
  - "Current max request rate: 10 requests/second" [AED].
  - "no more than 10 requests per second, regardless of the number of machines used to submit requests" [DEV][SEC-POL].
- **When exceeded:**
  - "we reserve the right to block IP addresses that submit excessive requests" [DEV][SEC-POL].
  - [SEC-POL] says excess requests "may be limited for a brief period", and access resumes "Once the rate of requests has dropped below the threshold for 10 minutes".
  - The **HTTP status code (403 or another) is [unverified]**: none of the fetched pages state it.
- **User-Agent:**
  - "Please declare your user agent in request headers" [AED].
  - The sample header has the form `User-Agent: <Sample Company Name> <admin contact email>`, together with `Accept-Encoding: gzip, deflate` and `Host: www.sec.gov` [AED].
  - The app must take the contact value from configuration at runtime and never hard-code it.
- **Bots:**
  - "unclassified" bots and automated tools are not allowed to crawl the site [DEV].
  - Use "efficient scripting… download only what you need… moderate requests" [AED][DEV].

## 6. CORS and caching

- "data.sec.gov does not support Cross Origin Resource Scripting (CORS)" [API]. The SEC wrote "Scripting", not "Sharing".
- Implication: browsers cannot call data.sec.gov directly, so all calls must go through our backend.
- Caching: no official caching guidance was found [AED][DEV][API].
  - Suggested TTLs, which are our own choice: submissions and facts for minutes to hours, `company_tickers.json` for about one day.

## 7. Update frequency [API][AED]

- "The JSON structures are updated throughout the day, in real time, as submissions are disseminated" [API].
- Processing delays [API], both of which "may be longer during peak filing times":
  - submissions: "typical processing delay of less than a second"
  - XBRL APIs (companyfacts, companyconcept, frames): "under a minute"
- Bulk ZIPs are "updated and republished nightly at approximately 3:00 a.m. ET" [API]:
  - `https://www.sec.gov/Archives/edgar/daily-index/xbrl/companyfacts.zip`
  - `https://www.sec.gov/Archives/edgar/daily-index/bulkdata/submissions.zip`
- Filing hours: "Monday through Friday, from 6:00 a.m. to 10:00 p.m., ET" [AED].
- Index updates [AED]:
  - Daily indexes are updated nightly from about 10:00 p.m. ET.
  - Full and quarterly indexes are rebuilt "weekly, early on Saturday mornings".
