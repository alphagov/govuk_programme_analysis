
# Intro

This is a simple script that scrapes the counts of 2xx, 3xx, 4xx and 5xx status codes for various apps from [GOV.UK graphite](https://graphite.publishing.service.gov.uk/). These counts are then saved as a .csv file with the format:
```
name, timestamp, 2xx, 3xx, 4xx, 5xx
```

## Requirements

This script requires python 2.7+ but only uses packages from the standard library (urllib2, datetime, json and csv).

## Installation

Either clone this directory:
```bash
git clone git@github.com:alphagov/govuk_programme_analysis.git
```

or copy just the [raw script](https://raw.githubusercontent.com/alphagov/govuk_programme_analysis/master/status_counts.py)


## Usage

This should be run from the terminal using python from this directory:
```bash
cd ~/govuk/govuk_programme_analysis # Or where ever you've copied the script
python status_counts.py
```

and produce output like:
```bash
Getting stats for:
    Whitehall frontend
    Manuals frontend
    Government frontend
[...]
    Whitehall Admin
    Content Store
Got data for 39 apps.
All done, 2017-04-04_status_code_report.csv created
```

## How it works

The script uses python to make a series of calls to graphite's [render API](http://graphite.readthedocs.io/en/latest/render_api.html). Using this API we can make graphite produce json output. The json is then parsed and written as a csv (the render API can natively produce csv but it is easier to work with json).

The API call to graphite uses several parameters & functions:

* **[from](http://graphite.readthedocs.io/en/latest/render_api.html#from-until)=-2weeks** The start of the window to produce output for (set to 2 weeks ago)
* **[until](http://graphite.readthedocs.io/en/latest/render_api.html#from-until)=-1weeks** The end of the window to produce output for (set to 1 week ago)
* **[target](http://graphite.readthedocs.io/en/latest/render_api.html#target)=** What we want to produce output for
    - **[sumSeries](http://graphite.readthedocs.io/en/latest/functions.html#graphite.render.functions.sumSeries)** Sum over the given array of values (this wraps the summarize function)
        + **[hitcount](http://graphite.readthedocs.io/en/latest/functions.html#graphite.render.functions.hitcount)** Estimate the counts of events recorded as rates in the stats-path.
            * *stats-path* which path to estimate for
            * *intervalString*: the interval to estimate for (value: 1week)
* **[format](http://graphite.readthedocs.io/en/latest/render_api.html#json)=json** We want json formatted output

### Graphite paths

Graphite uses .-deliminated paths to organise its metrics. For each app/status code combination we need to generate a path. To do this we split the graphite path into three sections:

* The host
* The app-path
* The status code

The hosts are of the form `stats.hostname-*.nginx_logs` where the hostname is something like `frontend` the `*` is a [wildcard](http://graphite.readthedocs.io/en/latest/render_api.html#target) that indicates to graphite that it should aggregate over all of the hosts of that name (for example `frontend-1`, `frontend-2`). The app-path is the full name of the app (for example `calculators_publishing_service_gov_uk`) and the status code is, for example: `http_2xx`.


## The apps

* Metadata API
* Asset Manager
* Collections Publisher
* Contacts Admin
* Content API
* Content performance manager
* Content Tagger
* Email Alert Api
* HMRC manuals API
* Imminence
* Local links manager
* Manuals Publisher
* Maslow
* Need API
* Policy Publisher
* Publisher
* Publishing API
* Release
* Search admin
* Short URL manager
* Signon
* Specialist publisher
* Specialist Publisher
* Support (api)
* Transition
* Travel advice publisher
* Content Store
* Calculators frontend
* Calendars frontend
* Smartanswers frontend
* Feedex (support form)/Feedback
* Government frontend
* Info frontend
* Manuals frontend
* Specialist frontend
* Mapit
* Rummager (search API)
* Whitehall Admin
* Whitehall frontend

## Not currently included

* Info pages frontend - this doesn't seem to exist as a separate app.
* Feedback forms - this doesn't seem to exist as a separate app.
* Bouncer - this produces status codes for a large number of domains (for example 'directgov' and 'businesslink') and it is unclear which statistics should be gathered for it.
