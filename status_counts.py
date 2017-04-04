#
# Status rates
#
# This queries the graphite render API (graphite.readthedocs.io/en/latest/render_api.html)
# to gather stats on the rates of 2xx and 5xx responses from various apps.
#

import urllib2
import json
import csv
import datetime


# "Info pages frontend" Doesn't exist?
# "Feedback forms" Doesn't exist?
# "Bouncer"=> what do 200's mean for a redirect system?

# Dict with the first level being hosts of the apps and the second being
# pretty print name/app name pairs. The * in the hosts means that graphite
# will summarise over all hosts with that name (e.g. api-1, api-2 & api-3)
apps = {
  # api-* hosts
  'stats.api-*_api.nginx_logs': {
    'Metadata API': 'metadata-api_publishing_service_gov_uk',
  },
  # backend-* hosts
  'stats.backend-*_backend.nginx_logs': {
    'Asset Manager': 'asset-manager_publishing_service_gov_uk',
    'Collections Publisher': 'collections-publisher_publishing_service_gov_uk',
    'Contacts Admin': 'contacts-admin_publishing_service_gov_uk',
    'Content API': 'contentapi_publishing_service_gov_uk',
    'Content performance manager': 'content-performance-manager_publishing_service_gov_uk',
    'Content Tagger': 'content-tagger_publishing_service_gov_uk',
    'Email Alert Api': 'email-alert-api_publishing_service_gov_uk',
    'HMRC manuals API': 'hmrc-manuals-api_publishing_service_gov_uk',
    'Imminence': 'imminence_publishing_service_gov_uk',
    'Local links manager': 'local-links-manager_publishing_service_gov_uk',
    'Manuals Publisher': 'manuals-publisher_publishing_service_gov_uk',
    'Maslow': 'maslow_publishing_service_gov_uk',
    'Need API': 'need-api_publishing_service_gov_uk',
    'Policy Publisher': 'policy-publisher_publishing_service_gov_uk',
    'Publisher': 'publisher_publishing_service_gov_uk',
    'Publishing API': 'publishing-api_publishing_service_gov_uk',
    'Release': 'release_publishing_service_gov_uk',
    'Search admin': 'search-admin_publishing_service_gov_uk',
    'Short URL manager': 'short-url-manager_publishing_service_gov_uk',
    'Signon': 'signon_publishing_service_gov_uk',
    'Specialist publisher': 'specialist-publisher_publishing_service_gov_uk',
    'Specialist Publisher': 'specialist-publisher_publishing_service_gov_uk',
    'Support (api)': 'support-api_publishing_service_gov_uk',
    'Transition': 'transition_publishing_service_gov_uk',
    'Travel advice publisher': 'travel-advice-publisher_publishing_service_gov_uk',
  },
  # content-store-* hosts
  'stats.content-store-*_api.nginx_logs': {
    'Content Store': 'content-store_publishing_service_gov_uk',
  },
  # content-store-* hosts
  'stats.calculators-frontend-1_frontend.nginx_logs': {
    'Calculators frontend': 'calculators_publishing_service_gov_uk',
    'Calendars frontend': 'calendars_publishing_service_gov_uk',
    'Smartanswers frontend': 'smartanswers_publishing_service_gov_uk',
  },
  # frontend-* hosts
  'stats.frontend-*_frontend.nginx_logs': {
    'Feedex (support form)/Feedback': 'feedback_publishing_service_gov_uk',
    'Government frontend': 'government-frontend_publishing_service_gov_uk',
    'Info frontend': 'info-frontend_publishing_service_gov_uk',
    'Manuals frontend': 'manuals-frontend_publishing_service_gov_uk',
    'Specialist frontend': 'specialist-frontend_publishing_service_gov_uk',
  },
  # mapit-* hosts
  'stats.mapit-*_api.nginx_logs': {
    'Mapit': 'mapit_publishing_service_gov_uk',
  },
  # search-* hosts (for rummager)
  'stats.search-*_api.nginx_logs': {
    'Rummager (search API)': 'rummager_publishing_service_gov_uk',
  },
  # whitehall-backend-* hosts
  'stats.whitehall-backend-*_backend.nginx_logs': {
    'Whitehall Admin': 'whitehall-admin_publishing_service_gov_uk',
  },
  # whitehall-frontend-* hosts
  'stats.whitehall-frontend-*_frontend.nginx_logs': {
    'Whitehall frontend': 'whitehall-frontend_publishing_service_gov_uk',
  },
}

def get_app_stats():
  res = []
  for host_path, hosts_apps in apps.items():
    for app_name, app_path in hosts_apps.items():
      rates = { 'name': app_name }
      print '\t%s'%app_name
      for code in ['2xx', '3xx', '4xx', '5xx']:
        data = get_stats_for(host_path, app_path, code)
        rates[code] = data['value']
        if data['timestamp'] and data['timestamp'] > 0:
          rates['timestamp'] = data['timestamp']

      # convert the timestamp to a more friendly format
      rates['timestamp'] = datetime.datetime.fromtimestamp(
        rates['timestamp']
      ).strftime('%Y-%m-%d %H:%M:%S')
      res.append(rates)
  return res


def get_stats_for(host_path, app_path, status_suffix):
  url = get_url(host_path, app_path, status_suffix)
  response = urllib2.urlopen(url)
  data = json.load(response)
  if len(data) == 0:
    return {'value': None, 'timestamp': None}
  return {
    'value': data[0][u'datapoints'][0][0],
    'timestamp': data[0][u'datapoints'][0][1],
  }


def get_url(host_path, app_path, status_suffix):
  path = '.'.join([host_path, app_path, 'http_' + status_suffix])
  return ''.join(['https://graphite.publishing.service.gov.uk', # Base URL
          '/render?',           # Use the render API
          'from=-2weeks&',      # Start of the window
          'until=-1weeks&',     # End of the window
          'target=sumSeries(',  # Create a single value (summed over all servers)
            'hitcount(',        # Estimate the count
              path, ',',        # The set of stats we want
              '"1week"',       # The window we're using
          '))&',                # Close
          'format=json'         # We want json
        ])

def write_csv(data):
  filename = datetime.date.today().isoformat() + '_status_code_report.csv'
  with open(filename, 'w') as out_file:
    fieldnames = ['name', 'timestamp', '2xx', '3xx', '4xx', '5xx']
    writer = csv.DictWriter(out_file, fieldnames)

    writer.writeheader()
    writer.writerows(data)

  return filename

if __name__ == '__main__':
  print 'Getting stats for:'
  data = get_app_stats()
  print 'Got data for %i apps.'%len(data)
  filename = write_csv(data)
  print 'All done, %s created'%filename
