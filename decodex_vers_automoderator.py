# -*- coding: utf-8 -*-
import urllib.request
import json
import re

decodex_url = "https://www.lemonde.fr/webservice/decodex/updates" 

data = {
  'satirical': {
    'urls': [],
    'message': "Pour information, {{match}} est satirique et à lire au second degré.",
    'report': False,
  },
  'complotist': {
    'urls': [],
    'message': "Attention, {{match}} diffuse des fausses actualités. Essayez de trouver une autre source ou remontez à l'origine de l'information.",
    'report': True,
  },
  'dubious': {
    'urls': [],
    'message': "Le lien {{match}} est questionnable. Essayez de trouver une autre source ou remontez à l'origine de l'information.",
    'report': True,
  }
}

# Don't know whether the Python will be an ordered dict or not
categories = ["satirical", "complotist", "dubious"]

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

# Put each site URL into its category
for siteID, site in sites.items():
  # Site without any URL
  if len(site) < 5:
    continue

  note = min(4, max(1, int(site[0])))

  # Ignore websites which are not a source (such as Reddit)
  if note == 4:
    continue

  #notule = site[1]
  #site_name = site[2]
  #slug = site[3]
  urls = site[4]
  category = categories[note-1]
  data_category = data[category]

  # Add URls
  data_category['urls'] += urls

ruleIDInc = 30

for category in categories:
  data_category = data[category]

  urls = data_category['urls']
  sites = ", ".join(map(lambda url: "'(^|[^a-z0-9\-])(%s)'" % re.escape(url), urls))
  message = data_category['message']

  rule = """
---

    # [%(ruleIDInc)s] Decodex %(category)s
    title+body+url (regex): [%(sites)s]
    moderators_exempt: false"""

  if data_category['report']:
    rule += """
    action: report
    action_reason: "Automod [%(ruleIDInc)s]: Decodex %(category)s\""""

  rule += """
    comment: |
      %(message)s

      [Source Décodex](https://www.lemonde.fr/verification/)."""


  print(rule % {
    'ruleIDInc': ruleIDInc,
    'category':  category,
    'sites':     sites,
    'message':   message,
  })

  ruleIDInc += 1
