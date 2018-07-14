# -*- coding: utf-8 -*-
import urllib.request
import json
import re

decodex_url = "https://www.lemonde.fr/webservice/decodex/updates" 
categories = ["satirical", "complotist", "dubious"]
messages = [
  "Pour information, « %(site_name)s » est un site satirique à lire au second degré.",
  "Attention, « %(site_name)s » diffuse des fausses actualités. Essayez de trouver une autre source ou remontez à l'origine de l'information.",
  "Le site « %(site_name)s » est questionnable. Essayez de trouver une autre source ou remontez à l'origine de l'information.",
]

# Load the Decodex Data
decodex = json.loads(urllib.request.urlopen(decodex_url).read().decode('utf-8'))
sites = decodex["sites"]
urls = decodex["urls"]

# Put the URLs in the sites objects
# (the model makes more sense like this)
for url, siteID in urls.items():
  site = sites[str(siteID)]

  # If it's the first URL to be added to the site,
  # create the list 
  if len(site) < 5:
    site.append([])

  site[4].append(url)

for siteID, site in sites.items():
  # Site without any URL
  if len(site) < 5:
    continue

  note = min(4, max(1, int(site[0])))

  # Ignore websites which are not a source
  if note == 4:
    continue

  notule = site[1]
  site_name = site[2]
  slug = site[3]
  urls = site[4]
  category = categories[note-1]
  message = messages[note-1] % { 'site_name': site_name }

  # The ruleID for automoderator
  ruleID = '9'+siteID

  sitesRegexp = ", ".join(map(lambda url: "'(^|[^a-z0-9\-])%s'" % re.escape(url), urls))

  rule = """---
    # [%(ruleID)s] Decodex %(category)s %(slug)s
    domain+body+title (regex): [%(sitesRegexp)s]
    comment: |
      %(message)s

      L'avis du [DÉCODEX](https://www.lemonde.fr/verification/):

      > %(notule)s
""" % {
  'ruleID':      ruleID,
  'category':    category,
  'slug':        slug,
  'sitesRegexp': sitesRegexp,
  'message':     message,
  'notule':      notule
  }

  print(rule)
